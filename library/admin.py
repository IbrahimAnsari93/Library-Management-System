from django.contrib import admin
from .models import Student, Book, Issue


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "roll_no", "email", "phone")
    search_fields = ("name", "roll_no", "email", "phone")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn")
    search_fields = ("title", "author", "isbn")


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "book",
        "issue_date",
        "due_date",
        "return_date",
        "returned",
        "fine",
    )

    list_filter = (
        "returned",
        "issue_date",
        "due_date",
    )

    search_fields = (
        "student__name",
        "student__roll_no",
        "book__title",
    )
