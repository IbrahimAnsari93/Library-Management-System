from django.db import models
from django.utils import timezone


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(
        max_length=20,
        unique=True
    )
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)

    isbn = models.CharField(
        max_length=50,
        unique=True
    )

    category = models.CharField(
        max_length=100,
        default="General"
    )

    publisher = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    publication_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    language = models.CharField(
        max_length=50,
        default="English"
    )

    edition = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    description = models.TextField(
        blank=True,
        default=""
    )

    shelf_number = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    rack_number = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    cover_image = models.ImageField(
        upload_to="books/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title

    @property
    def issued_quantity(self):
        return self.issue_set.filter(
            returned=False
        ).count()

    @property
    def available_quantity(self):
        return max(
            self.quantity - self.issued_quantity,
            0
        )

    @property
    def inventory_status(self):
        if self.available_quantity <= 0:
            return "Out of Stock"

        if self.available_quantity <= 2:
            return "Low Stock"

        return "In Stock"

    @property
    def is_low_stock(self):
        return (
            self.available_quantity > 0
            and self.available_quantity <= 2
        )

    @property
    def issue_percentage(self):
        if self.quantity <= 0:
            return 0

        return round(
            (self.issued_quantity / self.quantity) * 100
        )


class Issue(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    issue_date = models.DateField(
        auto_now_add=True
    )

    due_date = models.DateField()

    return_date = models.DateField(
        null=True,
        blank=True
    )

    returned = models.BooleanField(
        default=False
    )

    fine = models.PositiveIntegerField(
        default=0
    )

    @property
    def late_days(self):
        """
        Calculate number of late days.

        For an active issue:
        today's date is compared with due date.

        For a returned book:
        return date is compared with due date.
        """

        today = timezone.localdate()

                               
        if self.returned and self.return_date:

            if self.return_date > self.due_date:
                return (
                    self.return_date - self.due_date
                ).days

            return 0

                              
        if today > self.due_date:
            return (
                today - self.due_date
            ).days

        return 0

    @property
    def current_fine(self):
        """
        Current dynamic fine.

        Library policy:
        ₹10 per late day.
        """

        return self.late_days * 10

    @property
    def status(self):
        """
        Return current issue status.
        """

        if self.returned:
            return "Returned"

        if timezone.localdate() > self.due_date:
            return "Late"

        return "Issued"

    def __str__(self):
        return (
            f"{self.student.name} - "
            f"{self.book.title}"
        )


class FinePayment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("UPI", "UPI"),
        ("Card", "Card"),
        ("Bank Transfer", "Bank Transfer"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Partial", "Partial"),
        ("Paid", "Paid"),
    ]

    issue = models.OneToOneField(
        Issue,
        on_delete=models.CASCADE,
        related_name="fine_payment"
    )

    fine_amount = models.PositiveIntegerField(
        default=0
    )

    paid_amount = models.PositiveIntegerField(
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending"
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        default=""
    )

    payment_date = models.DateField(
        null=True,
        blank=True
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    notes = models.TextField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def pending_amount(self):
        return max(
            self.fine_amount - self.paid_amount,
            0
        )

    def update_status(self):
        if self.paid_amount <= 0:

            self.payment_status = "Pending"

        elif self.paid_amount < self.fine_amount:

            self.payment_status = "Partial"

        else:

            self.payment_status = "Paid"

        self.save(
            update_fields=[
                "payment_status",
                "updated_at",
            ]
        )

    def __str__(self):
        return (
            f"{self.issue.student.name} - "
            f"₹{self.fine_amount}"
        )


class Notification(models.Model):

    NOTIFICATION_TYPE_CHOICES = [
        ("overdue", "Overdue Book"),
        ("due_soon", "Due Soon"),
        ("low_stock", "Low Stock"),
        ("out_of_stock", "Out of Stock"),
        ("fine", "Pending Fine"),
    ]

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
