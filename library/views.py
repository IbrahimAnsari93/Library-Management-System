from io import BytesIO
import csv
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from .forms import BookForm, StudentForm
from .models import (
    Book,
    FinePayment,
    Issue,
    Student,
    Notification,
)


def login_view(request):

    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect("dashboard")

        return redirect("student_dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            if user.is_staff:
                return redirect("dashboard")

            return redirect(
                "student_dashboard"
            )

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "login.html"
    )


@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


                                                              
                 
                                                              

@login_required
def dashboard(request):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    today = timezone.localdate()

                                                                  
                      
                                                                  

    total_books = Book.objects.count()

    total_students = Student.objects.count()

    total_issues = Issue.objects.count()

    active_issues = Issue.objects.filter(
        returned=False
    ).count()

    returned_books = Issue.objects.filter(
        returned=True
    ).count()

    overdue_books = Issue.objects.filter(
        returned=False,
        due_date__lt=today
    ).count()

                                                                  
                          
                                                                  

    books = Book.objects.all()

    total_copies = sum(
        book.quantity
        for book in books
    )

    available_copies = sum(
        book.available_quantity
        for book in books
    )

    issued_copies = max(
        total_copies - available_copies,
        0
    )

    if total_copies > 0:

        utilization_percentage = round(
            (issued_copies / total_copies) * 100
        )

    else:

        utilization_percentage = 0

                                                                  
                  
                                                                  

    total_fine = sum(
        issue.fine or 0
        for issue in Issue.objects.all()
    )

    total_collected = sum(
        payment.paid_amount or 0
        for payment in FinePayment.objects.all()
    )

    total_outstanding = max(
        total_fine - total_collected,
        0
    )

    outstanding_fine = sum(
        issue.late_days * 10
        for issue in Issue.objects.filter(
            returned=False,
            due_date__lt=today
        )
    )

                                                                  
                       
                                                                  

    recent_issues = (
        Issue.objects
        .select_related(
            "student",
            "book"
        )
        .order_by(
            "-issue_date",
            "-id"
        )[:8]
    )

    recent_books = (
        Book.objects
        .order_by(
            "-created_at"
        )[:8]
    )

                                                                  
                        
                                                                  

    overdue_issues = (
        Issue.objects
        .filter(
            returned=False,
            due_date__lt=today
        )
        .select_related(
            "student",
            "book"
        )
        .order_by(
            "due_date"
        )[:8]
    )

                                                                  
                              
                                                                  

    overdue_chart_issues = (
        Issue.objects
        .filter(
            returned=False,
            due_date__lt=today
        )
        .select_related(
            "student",
            "book"
        )
        .order_by(
            "due_date"
        )
    )

    overdue_labels = []

    overdue_days = []

    for issue in overdue_chart_issues:

        overdue_labels.append(
            issue.book.title
        )

        overdue_days.append(
            issue.late_days
        )

                                                                  
                                  
                                                                  

    monthly_labels = []

    monthly_issued = []

    monthly_returned = []

    for month in range(1, 13):

        month_name = date(
            today.year,
            month,
            1
        ).strftime("%b")

        monthly_labels.append(
            month_name
        )

        monthly_issued.append(
            Issue.objects.filter(
                issue_date__year=today.year,
                issue_date__month=month
            ).count()
        )

        monthly_returned.append(
            Issue.objects.filter(
                return_date__year=today.year,
                return_date__month=month
            ).count()
        )                                                                                                                             

    in_stock_count = 0

    low_stock_count = 0

    out_of_stock_count = 0

    for book in books:

        if book.available_quantity <= 0:

            out_of_stock_count += 1

        elif book.available_quantity <= 2:

            low_stock_count += 1

        else:

            in_stock_count += 1

                                                                  
                   
                                                                  

    generate_notifications()

    unread_notification_count = (
        Notification.objects
        .filter(
            is_read=False
        )
        .count()
    )

                                                                  
                         
                                                                  

                                                                  
                      
                                                                  

    top_books = (
        Issue.objects
        .values(
            "book__title"
        )
        .annotate(
            issue_count=Count("id")
        )
        .order_by(
            "-issue_count"
        )[:6]
    )

    top_books_labels = [
        item["book__title"]
        for item in top_books
    ]

    top_books_data = [
        item["issue_count"]
        for item in top_books
    ]

                                                                  
                         
                                                                  

    top_students = (
        Issue.objects
        .values(
            "student__name"
        )
        .annotate(
            issue_count=Count("id")
        )
        .order_by(
            "-issue_count"
        )[:6]
    )

    top_students_labels = [
        item["student__name"]
        for item in top_students
    ]

    top_students_data = [
        item["issue_count"]
        for item in top_students
    ]

                                                                  
                           
                                                                  

    category_data = (
        Book.objects
        .values(
            "category"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "category"
        )
    )

    category_labels = [
        item["category"]
        for item in category_data
        if item["category"]
    ]

    category_values = [
        item["total"]
        for item in category_data
        if item["category"]
    ]

                                                                  
                    
                                                                  

    payment_status_query = (
        FinePayment.objects
        .values(
            "payment_status"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "payment_status"
        )
    )

    payment_status_labels = [
        item["payment_status"]
        for item in payment_status_query
    ]

    payment_status_values = [
        item["total"]
        for item in payment_status_query
    ]

                                                                  
             
                                                                  

    context = {

                                                                  
                          
                                                                  

        "today": today,

        "total_books": total_books,

        "total_students": total_students,

        "total_issues": total_issues,

        "active_issues": active_issues,

        "returned_books": returned_books,

        "overdue_books": overdue_books,

                                                                  
                   
                                                                  

        "total_copies": total_copies,

        "available_copies": available_copies,

        "issued_copies": issued_copies,

        "utilization_percentage": utilization_percentage,

                                                                  
                      
                                                                  

        "total_fine": total_fine,

        "total_collected": total_collected,

        "total_outstanding": total_outstanding,

        "outstanding_fine": outstanding_fine,

                                                                  
                     
                                                                  

        "recent_issues": recent_issues,

        "recent_books": recent_books,

        "overdue_issues": overdue_issues,

                                                                  
                       
                                                                  

        "overdue_labels": overdue_labels,

        "overdue_days": overdue_days,

                                                                  
                       
                                                                  

        "monthly_labels": monthly_labels,

        "monthly_issued": monthly_issued,

        "monthly_returned": monthly_returned,

                                                                  
                                
                                                                  

        "in_stock_count": in_stock_count,

        "low_stock_count": low_stock_count,

        "out_of_stock_count": out_of_stock_count,

                                                                  
                         
                                                                  

        "top_books_labels": top_books_labels,

        "top_books_data": top_books_data,

                                                                  
                            
                                                                  

        "top_students_labels": top_students_labels,

        "top_students_data": top_students_data,

                                                                  
                        
                                                                  

        "category_labels": category_labels,

        "category_values": category_values,

                                                                  
                              
                                                                  

        "payment_status_labels": payment_status_labels,

        "payment_status_data": payment_status_values,

                                                                  
                       
                                                                  

        "unread_notification_count": unread_notification_count,
    }

                                                                  
                      
                                                                  

    return render(
        request,
        "dashboard.html",
        context
    )
                                                              
                   
                                                              

@login_required
def student_dashboard(request):

    if request.user.is_staff:
        return redirect("dashboard")

    student = Student.objects.filter(
        email__iexact=request.user.email
    ).first()

    if student:

        my_issues = (
            Issue.objects
            .filter(
                student=student
            )
            .select_related(
                "book"
            )
            .order_by(
                "-issue_date",
                "-id"
            )
        )

    else:

        my_issues = Issue.objects.none()

    active_issues = my_issues.filter(
        returned=False
    )

    returned_issues = my_issues.filter(
        returned=True
    )

    today = timezone.localdate()

    overdue_issues = active_issues.filter(
        due_date__lt=today
    )

    outstanding_fine = sum(
        (issue.late_days * 10)
        for issue in overdue_issues
    )

    context = {

        "student":
            student,

        "my_issues":
            my_issues[:10],

        "active_issues":
            active_issues.count(),

        "returned_issues":
            returned_issues.count(),

        "overdue_issues":
            overdue_issues.count(),

        "outstanding_fine":
            outstanding_fine,
    }

    return render(
        request,
        "student_dashboard.html",
        context
    )


                                                              
              
                                                              

@login_required
def student_list(request):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    query = request.GET.get(
        "q",
        ""
    ).strip()

    students = (
        Student.objects
        .all()
        .order_by(
            "name"
        )
    )

    if query:

        students = students.filter(
            Q(name__icontains=query)
            |
            Q(roll_no__icontains=query)
            |
            Q(email__icontains=query)
            |
            Q(phone__icontains=query)
        )

    paginator = Paginator(
        students,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        "student_list.html",
        {
            "students": page_obj,
            "query": query,
        }
    )


                                                              
             
                                                              

@login_required
def student_add(request):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    if request.method == "POST":

        form = StudentForm(
            request.POST
        )

        if form.is_valid():

            student = form.save()

            messages.success(
                request,
                f"Student '{student.name}' added successfully."
            )

            return redirect(
                "student_list"
            )

    else:

        form = StudentForm()

    return render(
        request,
        "student_form.html",
        {
            "form": form,
            "page_title": "Add Student",
        }
    )


                                                              
                
                                                              

@login_required
def student_detail(request, id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    student = get_object_or_404(
        Student,
        id=id
    )

    issues = (
        Issue.objects
        .filter(
            student=student
        )
        .select_related(
            "book"
        )
        .order_by(
            "-issue_date",
            "-id"
        )
    )

    active_issues = issues.filter(
        returned=False
    )

    returned_issues = issues.filter(
        returned=True
    )

    today = timezone.localdate()

    overdue_issues = active_issues.filter(
        due_date__lt=today
    )

    outstanding_fine = sum(
        (issue.late_days * 10)
        for issue in overdue_issues
    )

    context = {

        "student":
            student,

        "issues":
            issues,

        "active_issues":
            active_issues,

        "returned_issues":
            returned_issues,

        "overdue_issues":
            overdue_issues,

        "outstanding_fine":
            outstanding_fine,
    }

    return render(
        request,
        "student_detail.html",
        context
    )


                                                              
              
                                                              

@login_required
def student_edit(request, id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    student = get_object_or_404(
        Student,
        id=id
    )

    if request.method == "POST":

        form = StudentForm(
            request.POST,
            instance=student
        )

        if form.is_valid():

            student = form.save()

            messages.success(
                request,
                f"Student '{student.name}' updated successfully."
            )

            return redirect(
                "student_detail",
                id=student.id
            )

    else:

        form = StudentForm(
            instance=student
        )

    return render(
        request,
        "student_form.html",
        {
            "form": form,
            "page_title": "Edit Student",
            "student": student,
        }
    )


                                                              
                
                                                              

@login_required
def student_delete(request, id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    student = get_object_or_404(
        Student,
        id=id
    )

    if request.method == "POST":

        student_name = student.name

        student.delete()

        messages.success(
            request,
            f"Student '{student_name}' deleted successfully."
        )

        return redirect(
            "student_list"
        )

    return render(
        request,
        "student_confirm_delete.html",
        {
            "student": student,
        }
    )


                                                              
           
                                                              

                                                              
                             
                                                              

@login_required
def book_list(request):

                                                              
                    
                                                              

    if not request.user.is_staff:
        return redirect("student_dashboard")

                                                              
                       
                                                              

    query = request.GET.get(
        "q",
        ""
    ).strip()

    category = request.GET.get(
        "category",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

                                                              
               
                                                              

    books = (
        Book.objects
        .all()
        .order_by(
            "-created_at"
        )
    )

                                                              
            
                                                  
                                                              

    if query:

        books = books.filter(
            Q(title__icontains=query)
            |
            Q(author__icontains=query)
            |
            Q(isbn__icontains=query)
            |
            Q(category__icontains=query)
            |
            Q(publisher__icontains=query)
        )

                                                              
                     
                                                              

    if category:

        books = books.filter(
            category__iexact=category
        )

                                                              
                         
     
              
               
                  
                                                              

    if status:

        filtered_books = []

        for book in books:

            if book.inventory_status == status:

                filtered_books.append(
                    book
                )

        books = filtered_books

                                                              
                
                       
                                                              

    if not isinstance(
        books,
        list
    ):

        paginator = Paginator(
            books,
            12
        )

        page_number = request.GET.get(
            "page"
        )

        page_obj = paginator.get_page(
            page_number
        )

    else:

        page_obj = books

                                                              
                   
                                                              

    categories = (
        Book.objects
        .values_list(
            "category",
            flat=True
        )
        .distinct()
        .order_by(
            "category"
        )
    )

                                                              
             
                                                              

    context = {

        "books":
            page_obj,

        "query":
            query,

        "category":
            category,

        "status":
            status,

        "categories":
            categories,
    }

                                                              
            
                                                              

    return render(
        request,
        "book_list.html",
        context
    )


                                                              
             
                                                              

@login_required
def book_detail(request, id):

    book = get_object_or_404(
        Book,
        id=id
    )

    issues = (
        Issue.objects
        .filter(
            book=book
        )
        .select_related(
            "student"
        )
        .order_by(
            "-issue_date",
            "-id"
        )
    )

    active_issues = issues.filter(
        returned=False
    )

    returned_issues = issues.filter(
        returned=True
    )

    return render(
        request,
        "book_detail.html",
        {
            "book": book,
            "issues": issues,
            "active_issues": active_issues,
            "returned_issues": returned_issues,
        }
    )


                                                              
          
                                                              

@login_required
def add_book(request):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    if request.method == "POST":

        form = BookForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            book = form.save()

            messages.success(
                request,
                f"Book '{book.title}' added successfully."
            )

            return redirect(
                "book_list"
            )

    else:

        form = BookForm()

    return render(
        request,
        "book_form.html",
        {
            "form": form,
            "page_title": "Add Book",
        }
    )


                                                              
           
                                                              

@login_required
def edit_book(request, id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    book = get_object_or_404(
        Book,
        id=id
    )

    if request.method == "POST":

        form = BookForm(
            request.POST,
            request.FILES,
            instance=book
        )

        if form.is_valid():

            book = form.save()

            messages.success(
                request,
                f"Book '{book.title}' updated successfully."
            )

            return redirect(
                "book_detail",
                id=book.id
            )

    else:

        form = BookForm(
            instance=book
        )

    return render(
        request,
        "book_form.html",
        {
            "form": form,
            "page_title": "Edit Book",
            "book": book,
        }
    )


                                                              
             
                                                              

@login_required
def delete_book(request, id):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    book = get_object_or_404(
        Book,
        id=id
    )

    if request.method == "POST":

        book_title = book.title

        book.delete()

        messages.success(
            request,
            f"Book '{book_title}' deleted successfully."
        )

        return redirect(
            "book_list"
        )

    return render(
        request,
        "book_confirm_delete.html",
        {
            "book": book,
        }
    )


                                                              
                                  
                                                              

@login_required
def inventory_dashboard(request):

    if not request.user.is_staff:
        return redirect("student_dashboard")

    books = list(
        Book.objects.all()
    )

                                                              
                                            
                                                              

    inventory_query = request.GET.get(
        "q",
        ""
    ).strip()

    inventory_category = request.GET.get(
        "category",
        ""
    ).strip()

    inventory_status = request.GET.get(
        "status",
        ""
    ).strip()

    inventory_sort = request.GET.get(
        "sort",
        "title"
    ).strip()

    filtered_inventory_books = []

    for book in books:

        matches_query = True

        if inventory_query:
            search_text = (
                f"{book.title} "
                f"{book.author} "
                f"{book.isbn} "
                f"{book.category}"
            ).lower()

            matches_query = (
                inventory_query.lower()
                in search_text
            )

        matches_category = (
            not inventory_category
            or book.category == inventory_category
        )

        matches_status = (
            not inventory_status
            or book.inventory_status == inventory_status
        )

        if (
            matches_query
            and matches_category
            and matches_status
        ):
            filtered_inventory_books.append(book)

    if inventory_sort == "available":
        filtered_inventory_books.sort(
            key=lambda book: book.available_quantity,
            reverse=True
        )

    elif inventory_sort == "issued":
        filtered_inventory_books.sort(
            key=lambda book: book.issued_quantity,
            reverse=True
        )

    elif inventory_sort == "quantity":
        filtered_inventory_books.sort(
            key=lambda book: book.quantity,
            reverse=True
        )

    else:
        filtered_inventory_books.sort(
            key=lambda book: book.title.lower()
        )

    inventory_paginator = Paginator(
        filtered_inventory_books,
        10
    )

    inventory_page = inventory_paginator.get_page(
        request.GET.get("page")
    )

    inventory_categories = (
        Book.objects
        .values_list(
            "category",
            flat=True
        )
        .distinct()
        .order_by("category")
    )

    total_titles = len(
        books
    )

    total_copies = 0
    available_copies = 0
    issued_copies = 0

    low_stock_books = []
    out_of_stock_books = []

    in_stock_count = 0
    low_stock_count = 0
    out_of_stock_count = 0

                                                              
                           
                                                              

    for book in books:

        total_copies += book.quantity

        issued = book.issued_quantity

        available = book.available_quantity

        issued_copies += issued

        available_copies += available

        if available == 0:

            out_of_stock_books.append(
                book
            )

            out_of_stock_count += 1

        elif available <= 2:

            low_stock_books.append(
                book
            )

            low_stock_count += 1

        else:

            in_stock_count += 1

                                                              
                 
                                                              

    if total_copies > 0:

        utilization_percentage = round(
            (
                issued_copies
                / total_copies
            ) * 100
        )

    else:

        utilization_percentage = 0

                                                              
                       
                                                              

    most_issued_books = []

    for book in books:

        total_issues = (
            Issue.objects
            .filter(
                book=book
            )
            .count()
        )

        most_issued_books.append(
            {
                "book": book,
                "total_issues": total_issues,
            }
        )

    most_issued_books.sort(
        key=lambda item:
            item["total_issues"],
        reverse=True
    )

    most_issued_books = [
        item
        for item in most_issued_books
        if item["total_issues"] > 0
    ]

    most_issued_books = (
        most_issued_books[:10]
    )

                                                              
                            
                                                              

    most_issued_chart_data = {

        "labels": [
            item["book"].title
            for item in most_issued_books
        ],

        "authors": [
            item["book"].author
            for item in most_issued_books
        ],

        "values": [
            item["total_issues"]
            for item in most_issued_books
        ],
    }

                                
                                   

    total_issues_count = Issue.objects.count()

                                                              
                             
                                                              

    category_data = {}

    for book in books:

        category = (
            book.category
            or "General"
        )

        if category not in category_data:

            category_data[category] = {

                "title_count": 0,

                "total_copies": 0,

                "available_copies": 0,

                "issued_copies": 0,
            }

        category_data[category][
            "title_count"
        ] += 1

        category_data[category][
            "total_copies"
        ] += book.quantity

        category_data[category][
            "available_copies"
        ] += book.available_quantity

        category_data[category][
            "issued_copies"
        ] += book.issued_quantity

    category_inventory = []

    for category, data in category_data.items():

        category_inventory.append(
            {
                "category":
                    category,

                "title_count":
                    data["title_count"],

                "total_copies":
                    data["total_copies"],

                "available_copies":
                    data["available_copies"],

                "issued_copies":
                    data["issued_copies"],
            }
        )

    category_inventory.sort(
        key=lambda item:
            item["total_copies"],
        reverse=True
    )

                                                              
                  
                                                              

    recent_books = (
        Book.objects
        .order_by(
            "-created_at"
        )[:8]
    )

                                                              
                   
                                                              

    recent_issues = (
        Issue.objects
        .select_related(
            "student",
            "book"
        )
        .order_by(
            "-issue_date",
            "-id"
        )[:8]
    )

                                                              
             
                                                              

    today = timezone.localdate()

    overdue_issues = (
        Issue.objects
        .filter(
            returned=False,
            due_date__lt=today
        )
        .select_related(
            "student",
            "book"
        )
        .order_by(
            "due_date"
        )
    )

    overdue_count = (
        overdue_issues.count()
    )

    outstanding_fine = sum(
        (issue.late_days * 10)
        for issue in overdue_issues
    )

                                                              
                              
                                                              

    stock_chart_data = {

        "labels": [
            "In Stock",
            "Low Stock",
            "Out of Stock",
        ],

        "values": [
            in_stock_count,
            low_stock_count,
            out_of_stock_count,
        ],
    }

                                                              
             
                                                              

    context = {

        "total_titles":
            total_titles,

        "inventory_books":
            inventory_page,

        "inventory_query":
            inventory_query,

        "inventory_category":
            inventory_category,

        "inventory_status":
            inventory_status,

        "inventory_sort":
            inventory_sort,

        "inventory_categories":
            inventory_categories,

        "total_inventory_results":
            len(filtered_inventory_books),

        "total_copies":
            total_copies,

        "available_copies":
            available_copies,

        "issued_copies":
            issued_copies,

        "utilization_percentage":
            utilization_percentage,

        "low_stock_books":
            low_stock_books,

        "out_of_stock_books":
            out_of_stock_books,

        "low_stock_count":
            low_stock_count,

        "out_of_stock_count":
            out_of_stock_count,

        "in_stock_count":
            in_stock_count,

        "stock_chart_data":
            stock_chart_data,

        "most_issued_books":
            most_issued_books,

        "most_issued_chart_data":
            most_issued_chart_data,

        "total_issues_count":
            total_issues_count,

        "category_inventory":
            category_inventory,

        "recent_books":
            recent_books,

        "recent_issues":
            recent_issues,

        "overdue_issues":
            overdue_issues[:10],

        "overdue_count":
            overdue_count,

        "outstanding_fine":
            outstanding_fine,
    }

    return render(
        request,
        "inventory_dashboard.html",
        context
    )

                                                              
            
                                                              

@login_required
def issue_book(request):

                                      
    if not request.user.is_staff:
        return redirect("student_dashboard")

    students = Student.objects.all().order_by("name")

    books = Book.objects.all().order_by("title")

    if request.method == "POST":

        student_id = request.POST.get("student")
        book_id = request.POST.get("book")
        due_date_value = request.POST.get("due_date")

                                                              
                     
                                                              

        student = get_object_or_404(
            Student,
            id=student_id
        )

                                                              
                  
                                                              

        book = get_object_or_404(
            Book,
            id=book_id
        )

                                                              
                                 
                                                              

        active_issues = Issue.objects.filter(
            book=book,
            returned=False
        ).count()

        if active_issues >= book.quantity:
            messages.error(
                request,
                "This book is currently unavailable."
            )

            return redirect("issue_book")

                                                              
                           
                                                              

        try:

            due_date = date.fromisoformat(
                due_date_value
            )

        except (TypeError, ValueError):

            messages.error(
                request,
                "Please enter a valid due date."
            )

            return redirect("issue_book")

                                                              
               
                                                              

        today = timezone.localdate()

        if due_date < today:

            messages.error(
                request,
                "Due date cannot be before today."
            )

            return redirect("issue_book")

                                                              
                                      
                                                              

        already_issued = Issue.objects.filter(
            student=student,
            book=book,
            returned=False
        ).exists()

        if already_issued:

            messages.error(
                request,
                "This student already has this book issued."
            )

            return redirect("issue_book")

                                                              
                      
                                                              

        Issue.objects.create(
            student=student,
            book=book,
            issue_date=today,
            due_date=due_date,
            returned=False,
            fine=0
        )

                                                              
                         
                                                              

        messages.success(
            request,
            f"Book issued successfully to {student.name}."
        )

        return redirect("issue_list")

                                                              
               
                                                              

    context = {
        "students": students,
        "books": books,
        "today": timezone.localdate(),
        "default_due_date": (
            timezone.localdate() + timedelta(days=14)
        ),
    }

    return render(
        request,
        "issue_form.html",
        context
    )


                                                              
            
                                                              

@login_required
def issue_list(request):

                                                
    if not request.user.is_staff:
        return redirect("student_dashboard")

    today = timezone.localdate()

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    status_filter = request.GET.get(
        "status",
        ""
    ).strip()

    issues = (
        Issue.objects
        .select_related(
            "student",
            "book"
        )
        .all()
        .order_by(
            "-issue_date",
            "-id"
        )
    )

                                                              
            
                                                              

    if search_query:

        issues = issues.filter(
            Q(student__name__icontains=search_query)
            |
            Q(student__roll_no__icontains=search_query)
            |
            Q(book__title__icontains=search_query)
            |
            Q(book__author__icontains=search_query)
        )

                                                              
                   
                                                              

    if status_filter == "Issued":

        issues = issues.filter(
            returned=False,
            due_date__gte=today
        )

    elif status_filter == "Late":

        issues = issues.filter(
            returned=False,
            due_date__lt=today
        )

    elif status_filter == "Returned":

        issues = issues.filter(
            returned=True
        )

                                                              
                    
                                                              

    total_count = Issue.objects.count()

    active_count = Issue.objects.filter(
        returned=False
    ).count()

    late_count = Issue.objects.filter(
        returned=False,
        due_date__lt=today
    ).count()

    returned_count = Issue.objects.filter(
        returned=True
    ).count()

                                                              
                
                                                              

    paginator = Paginator(
        issues,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

                                                              
             
                                                              

    context = {

        "issues": page_obj,

        "page_obj": page_obj,

        "search_query": search_query,

        "status_filter": status_filter,

        "total_count": total_count,

        "active_count": active_count,

        "late_count": late_count,

        "returned_count": returned_count,
    }

    return render(
        request,
        "issue_list.html",
        context
    )


                                                              
             
                                                              

@login_required
def return_book(request, id):

                                          
    if not request.user.is_staff:
        return redirect("student_dashboard")

    issue = get_object_or_404(
        Issue.objects.select_related(
            "student",
            "book"
        ),
        id=id
    )

                                                              
                      
                                                              

    if issue.returned:

        messages.warning(
            request,
            f'"{issue.book.title}" has already been returned.'
        )

        return redirect("issue_list")

                                                              
                    
                                                              

    if request.method == "POST":

        today = timezone.localdate()

                             
        if today > issue.due_date:

            late_days = (
                today - issue.due_date
            ).days

        else:

            late_days = 0

                                 
        fine_amount = late_days * 10

        issue.return_date = today
        issue.returned = True
        issue.fine = fine_amount

        issue.save(
            update_fields=[
                "return_date",
                "returned",
                "fine",
            ]
        )

                                                              
                         
                                                              

        if fine_amount > 0:

            messages.success(
                request,
                f'"{issue.book.title}" returned successfully. '
                f'Late by {late_days} day(s). '
                f'Fine: ₹{fine_amount}.'
            )

        else:

            messages.success(
                request,
                f'"{issue.book.title}" returned successfully. '
                f'No fine was charged.'
            )

        return redirect("issue_list")

                                                              
                 
                                                              

    return render(
        request,
        "return_book.html",
        {
            "issue": issue
        }
    )
                                                              
                                    
                                                              

@login_required
def return_book(request, id):

                                                              
                  
                                                              

    if not request.user.is_staff:
        return redirect("student_dashboard")

                                                              
               
                                                              

    issue = get_object_or_404(
        Issue.objects.select_related(
            "student",
            "book"
        ),
        id=id
    )

                                                              
                            
                                                              

    if issue.returned:

        messages.warning(
            request,
            f"'{issue.book.title}' has already been returned."
        )

        return redirect(
            "issue_list"
        )

                                                              
                    
                                                              

    if request.method == "POST":

        today = timezone.localdate()

                                                              
                             
                                                              

        if today > issue.due_date:

            late_days = (
                today - issue.due_date
            ).days

        else:

            late_days = 0

                                                              
                     
                          
                                                              

        fine_amount = late_days * 10

                                                              
                      
                                                              

        issue.return_date = today

        issue.returned = True

        issue.fine = fine_amount

        issue.save(
            update_fields=[
                "return_date",
                "returned",
                "fine",
            ]
        )

                                                              
                         
                                                              

        if fine_amount > 0:

            messages.success(
                request,
                f"'{issue.book.title}' returned successfully. "
                f"Late by {late_days} day(s). "
                f"Fine: ₹{fine_amount}."
            )

        else:

            messages.success(
                request,
                f"'{issue.book.title}' returned successfully. "
                f"No fine was charged."
            )

        return redirect(
            "issue_list"
        )

                                                              
                 
                            
                                                              

    return render(
        request,
        "return_book.html",
        {
            "issue": issue,
        }
    )
                                                              
                 
                                                              
@login_required
def fine_management(request):

                                                 
    if not request.user.is_staff:
        return redirect("student_dashboard")

    today = timezone.localdate()

    search_query = request.GET.get(
        "search",
        ""
    ).strip()

    status_filter = request.GET.get(
        "status",
        ""
    ).strip()

                                                       
                           
                                                       

    issues = (
        Issue.objects
        .select_related(
            "student",
            "book",
            "fine_payment"
        )
        .order_by(
            "-issue_date",
            "-id"
        )
    )

                                                       
            
                                                       

    if search_query:

        issues = issues.filter(
            Q(student__name__icontains=search_query)
            |
            Q(student__roll_no__icontains=search_query)
            |
            Q(book__title__icontains=search_query)
            |
            Q(book__isbn__icontains=search_query)
        )

                                                       
             
                                                       

    if status_filter == "fine":

        issues = issues.filter(
            fine__gt=0
        )

    elif status_filter == "no_fine":

        issues = issues.filter(
            fine=0
        )

    elif status_filter == "late":

        issues = issues.filter(
            returned=False,
            due_date__lt=today
        )

    elif status_filter == "returned":

        issues = issues.filter(
            returned=True,
            fine__gt=0
        )

                                                       
                     
                                                       

    all_fine_payments = FinePayment.objects.all()

    total_fine = sum(
        payment.fine_amount
        for payment in all_fine_payments
    )

    total_collected = sum(
        payment.paid_amount
        for payment in all_fine_payments
    )

    total_outstanding = sum(
        payment.pending_amount
        for payment in all_fine_payments
    )

    fine_records = FinePayment.objects.filter(
        fine_amount__gt=0
    ).count()

    paid_records = FinePayment.objects.filter(
        payment_status="Paid"
    ).count()

    partial_records = FinePayment.objects.filter(
        payment_status="Partial"
    ).count()

    pending_records = FinePayment.objects.filter(
        payment_status="Pending"
    ).count()

                                                       
                          
                                                       

    late_issues = Issue.objects.filter(
        returned=False,
        due_date__lt=today
    ).count()

                                                       
                
                                                       

    paginator = Paginator(
        issues,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

                                                       
             
                                                       

    context = {

        "issues": page_obj,

        "page_obj": page_obj,

        "search_query": search_query,

        "status_filter": status_filter,

                         
        "total_fine": total_fine,

        "total_collected": total_collected,

        "total_outstanding": total_outstanding,

        "fine_records": fine_records,

        "paid_records": paid_records,

        "partial_records": partial_records,

        "pending_records": pending_records,

        "late_issues": late_issues,
    }

    return render(
        request,
        "fine_management.html",
        context
    )


@login_required
def pay_fine(request, id):

                                              
    if not request.user.is_staff:
        return redirect("student_dashboard")

               
    issue = get_object_or_404(
        Issue.objects.select_related(
            "student",
            "book"
        ),
        id=id
    )

                              
    if issue.fine <= 0:
        messages.warning(
            request,
            "This issue does not have any fine."
        )
        return redirect("fine_management")

                                                    
    payment, created = FinePayment.objects.get_or_create(
        issue=issue,
        defaults={
            "fine_amount": issue.fine,
            "paid_amount": 0,
            "payment_status": "Pending",
        }
    )

                                              
    if payment.fine_amount != issue.fine:

        payment.fine_amount = issue.fine

        if payment.paid_amount >= payment.fine_amount:
            payment.payment_status = "Paid"

        elif payment.paid_amount > 0:
            payment.payment_status = "Partial"

        else:
            payment.payment_status = "Pending"

        payment.save(
            update_fields=[
                "fine_amount",
                "payment_status",
                "updated_at",
            ]
        )

                           
    if payment.paid_amount >= payment.fine_amount:

        messages.info(
            request,
            "This fine has already been fully paid."
        )

        return redirect("fine_management")

                                                       
                 
                                                       

    if request.method == "GET":

        return render(
            request,
            "pay_fine.html",
            {
                "issue": issue,
                "payment": payment,
            }
        )

                                                       
                  
                                                       

    if request.method == "POST":

        amount_text = request.POST.get(
            "amount",
            ""
        ).strip()

        payment_method = request.POST.get(
            "payment_method",
            ""
        ).strip()

        transaction_id = request.POST.get(
            "transaction_id",
            ""
        ).strip()

        notes = request.POST.get(
            "notes",
            ""
        ).strip()

                                                       
                                 
                                                       

        try:

            amount = int(amount_text)

        except (TypeError, ValueError):

            messages.error(
                request,
                "Please enter a valid payment amount."
            )

            return render(
                request,
                "pay_fine.html",
                {
                    "issue": issue,
                    "payment": payment,
                }
            )

        if amount <= 0:

            messages.error(
                request,
                "Payment amount must be greater than ₹0."
            )

            return render(
                request,
                "pay_fine.html",
                {
                    "issue": issue,
                    "payment": payment,
                }
            )

                                                       
                              
                                                       

        pending_amount = payment.pending_amount

        if amount > pending_amount:

            messages.error(
                request,
                f"Payment cannot exceed the pending fine "
                f"of ₹{pending_amount}."
            )

            return render(
                request,
                "pay_fine.html",
                {
                    "issue": issue,
                    "payment": payment,
                }
            )

                                                       
                                 
                                                       

        valid_methods = {
            "Cash",
            "UPI",
            "Card",
            "Bank Transfer",
        }

        if payment_method not in valid_methods:

            messages.error(
                request,
                "Please select a valid payment method."
            )

            return render(
                request,
                "pay_fine.html",
                {
                    "issue": issue,
                    "payment": payment,
                }
            )

                                                       
                                             
                                                       

        digital_methods = {
            "UPI",
            "Card",
            "Bank Transfer",
        }

        if (
            payment_method in digital_methods
            and not transaction_id
        ):

            messages.error(
                request,
                "Transaction ID is required for digital payments."
            )

            return render(
                request,
                "pay_fine.html",
                {
                    "issue": issue,
                    "payment": payment,
                }
            )

                                                       
                      
                                                       

        payment.paid_amount += amount

        payment.payment_method = payment_method

        payment.payment_date = timezone.localdate()

        payment.transaction_id = transaction_id

        payment.notes = notes

                                                       
                               
                                                       

        if payment.paid_amount >= payment.fine_amount:

            payment.paid_amount = payment.fine_amount

            payment.payment_status = "Paid"

        elif payment.paid_amount > 0:

            payment.payment_status = "Partial"

        else:

            payment.payment_status = "Pending"

        payment.save()

                                                       
                         
                                                       

        if payment.payment_status == "Paid":

            messages.success(
                request,
                f"Fine of ₹{payment.fine_amount} "
                f"has been fully paid."
            )

        else:

            messages.success(
                request,
                f"₹{amount} payment recorded successfully. "
                f"Remaining fine: ₹{payment.pending_amount}."
            )

        return redirect("fine_management")

              
    return redirect("fine_management")
@login_required
def fine_receipt(request, id):
    if not request.user.is_staff:
        return redirect("student_dashboard")

    payment = get_object_or_404(
        FinePayment.objects.select_related(
            "issue__student",
            "issue__book"
        ),
        id=id
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="fine_receipt_{payment.id}.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "LIBRARY MANAGEMENT SYSTEM",
            styles["Title"]
        )
    )

    elements.append(
        Spacer(1, 15)
    )

    elements.append(
        Paragraph(
            "Fine Payment Receipt",
            styles["Heading2"]
        )
    )

    elements.append(
        Spacer(1, 15)
    )

    data = [
        ["Receipt ID", f"#{payment.id}"],
        ["Student Name", payment.issue.student.name],
        ["Roll Number", payment.issue.student.roll_no],
        ["Book", payment.issue.book.title],
        ["ISBN", payment.issue.book.isbn],
        ["Fine Amount", f"₹{payment.fine_amount}"],
        ["Paid Amount", f"₹{payment.paid_amount}"],
        ["Outstanding", f"₹{payment.pending_amount}"],
        ["Payment Status", payment.payment_status],
        [
            "Payment Method",
            payment.payment_method or "N/A"
        ],
        [
            "Transaction ID",
            payment.transaction_id or "N/A"
        ],
        [
            "Payment Date",
            str(payment.payment_date or "N/A")
        ],
        [
            "Notes",
            payment.notes or "N/A"
        ],
    ]

    table = Table(
        data,
        colWidths=[150, 330]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                "Helvetica"
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
        ])
    )

    elements.append(table)

    elements.append(
        Spacer(1, 25)
    )

    elements.append(
        Paragraph(
            "This is a computer-generated payment receipt.",
            styles["Normal"]
        )
    )

    document.build(elements)

    return response
                                                              
                 
                                                              
@login_required
def payment_history(request):
    if not request.user.is_staff:
        return redirect("student_dashboard")

    search_query = request.GET.get("search", "").strip()
    status_filter = request.GET.get("status", "").strip()
    method_filter = request.GET.get("method", "").strip()

    payments = (
        FinePayment.objects
        .select_related(
            "issue",
            "issue__student",
            "issue__book",
        )
        .order_by("-payment_date", "-created_at", "-id")
    )

    if search_query:
        payments = payments.filter(
            Q(issue__student__name__icontains=search_query)
            |
            Q(issue__student__roll_no__icontains=search_query)
            |
            Q(issue__book__title__icontains=search_query)
            |
            Q(issue__book__isbn__icontains=search_query)
            |
            Q(transaction_id__icontains=search_query)
        )

    if status_filter:
        payments = payments.filter(
            payment_status=status_filter
        )

    if method_filter:
        payments = payments.filter(
            payment_method=method_filter
        )

    total_records = payments.count()

    total_fine = sum(
        payment.fine_amount
        for payment in payments
    )

    total_paid = sum(
        payment.paid_amount
        for payment in payments
    )

    total_pending = sum(
        payment.pending_amount
        for payment in payments
    )

    paginator = Paginator(payments, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "payments": page_obj,
        "page_obj": page_obj,

        "search_query": search_query,
        "status_filter": status_filter,
        "method_filter": method_filter,

        "total_records": total_records,
        "total_fine": total_fine,
        "total_paid": total_paid,
        "total_pending": total_pending,

        "payment_methods": [
            "Cash",
            "UPI",
            "Card",
            "Bank Transfer",
        ],

        "payment_statuses": [
            "Pending",
            "Partial",
            "Paid",
        ],
    }

    return render(
        request,
        "payment_history.html",
        context
    )

                                                              
         
                                                              

@login_required
def reports(request):

                                         
    if not request.user.is_staff:
        return redirect("student_dashboard")

                               
                  
                               

    total_books = Book.objects.count()

    total_book_copies = sum(
        book.quantity
        for book in Book.objects.all()
    )

    total_students = Student.objects.count()

    total_issues = Issue.objects.count()

    active_issues = Issue.objects.filter(
        returned=False
    ).count()

    returned_books = Issue.objects.filter(
        returned=True
    ).count()

    late_books = Issue.objects.filter(
        returned=False,
        due_date__lt=timezone.localdate()
    ).count()

                               
                    
                               

    available_copies = sum(
        book.available_quantity
        for book in Book.objects.all()
    )

    issued_copies = max(
        total_book_copies - available_copies,
        0
    )

                               
                      
                               

    total_fine = sum(
        payment.fine_amount
        for payment in FinePayment.objects.all()
    )

    total_collected = sum(
        payment.paid_amount
        for payment in FinePayment.objects.all()
    )

    total_outstanding = sum(
        payment.pending_amount
        for payment in FinePayment.objects.all()
    )

                               
                    
                               

    paid_payments = FinePayment.objects.filter(
        payment_status="Paid"
    ).count()

    partial_payments = FinePayment.objects.filter(
        payment_status="Partial"
    ).count()

    pending_payments = FinePayment.objects.filter(
        payment_status="Pending"
    ).count()

                               
                      
                               

    top_books = (
        Book.objects
        .annotate(
            issue_count=Count("issue")
        )
        .order_by("-issue_count", "title")[:5]
    )

    top_books_labels = [
        book.title
        for book in top_books
    ]

    top_books_data = [
        book.issue_count
        for book in top_books
    ]

                               
                         
                               

    top_students = (
        Student.objects
        .annotate(
            issue_count=Count("issue")
        )
        .order_by("-issue_count", "name")[:5]
    )

    top_students_labels = [
        student.name
        for student in top_students
    ]

    top_students_data = [
        student.issue_count
        for student in top_students
    ]

                               
                     
                               

    category_data = {}

    for book in Book.objects.all():

        category = book.category or "General"

        category_data[category] = (
            category_data.get(category, 0)
            + book.quantity
        )

    category_labels = list(
        category_data.keys()
    )

    category_values = list(
        category_data.values()
    )

                               
                  
                               

    issue_status_labels = [
        "Active",
        "Returned",
        "Late",
    ]

    issue_status_data = [
        active_issues,
        returned_books,
        late_books,
    ]

                               
                    
                               

    payment_status_labels = [
        "Paid",
        "Partial",
        "Pending",
    ]

    payment_status_data = [
        paid_payments,
        partial_payments,
        pending_payments,
    ]

                               
                      
                               

    in_stock = 0
    low_stock = 0
    out_of_stock = 0

    for book in Book.objects.all():

        available = book.available_quantity

        if available <= 0:
            out_of_stock += 1

        elif available <= 2:
            low_stock += 1

        else:
            in_stock += 1

    inventory_labels = [
        "In Stock",
        "Low Stock",
        "Out of Stock",
    ]

    inventory_data = [
        in_stock,
        low_stock,
        out_of_stock,
    ]

                               
                          
                               

    monthly_issues = (
        Issue.objects
        .annotate(
            month=TruncMonth("issue_date")
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    monthly_issue_labels = [
        item["month"].strftime("%b %Y")
        for item in monthly_issues
        if item["month"]
    ]

    monthly_issue_data = [
        item["total"]
        for item in monthly_issues
        if item["month"]
    ]

                               
                           
                               

    monthly_returns = (
        Issue.objects
        .filter(
            returned=True,
            return_date__isnull=False
        )
        .annotate(
            month=TruncMonth("return_date")
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    monthly_return_labels = [
        item["month"].strftime("%b %Y")
        for item in monthly_returns
        if item["month"]
    ]

    monthly_return_data = [
        item["total"]
        for item in monthly_returns
        if item["month"]
    ]

                               
                             
                               

    monthly_payments = (
        FinePayment.objects
        .filter(
            payment_date__isnull=False
        )
        .annotate(
            month=TruncMonth("payment_date")
        )
        .values("month")
        .annotate(
            collected=Sum("paid_amount")
        )
        .order_by("month")
    )

    monthly_fine_labels = [
        item["month"].strftime("%b %Y")
        for item in monthly_payments
        if item["month"]
    ]

    monthly_fine_data = [
        item["collected"] or 0
        for item in monthly_payments
        if item["month"]
    ]

                                                                  
                              
                                                                  

    overdue_chart_issues = (
        Issue.objects
        .filter(
            returned=False,
            due_date__lt=timezone.localdate()
        )
        .select_related(
            "student",
            "book"
        )
        .order_by("due_date")
    )

    overdue_labels = []
    overdue_days = []

    for issue in overdue_chart_issues:
        overdue_labels.append(issue.book.title)
        overdue_days.append(issue.late_days)

                               
             
                               

    context = {

               
        "total_books": total_books,
        "total_book_copies": total_book_copies,
        "total_students": total_students,
        "total_issues": total_issues,

                     
        "active_issues": active_issues,
        "returned_books": returned_books,
        "late_books": late_books,

                   
        "available_copies": available_copies,
        "issued_copies": issued_copies,

              
        "total_fine": total_fine,
        "total_collected": total_collected,
        "total_outstanding": total_outstanding,

                  
        "paid_payments": paid_payments,
        "partial_payments": partial_payments,
        "pending_payments": pending_payments,

                   
        "top_books_labels": top_books_labels,
        "top_books_data": top_books_data,

                      
        "top_students_labels": top_students_labels,
        "top_students_data": top_students_data,

                  
        "category_labels": category_labels,
        "category_values": category_values,

                      
        "issue_status_labels": issue_status_labels,
        "issue_status_data": issue_status_data,

                        
        "payment_status_labels": payment_status_labels,
        "payment_status_data": payment_status_data,

                   
        "inventory_labels": inventory_labels,
        "inventory_data": inventory_data,

                        
        "monthly_issue_labels": monthly_issue_labels,
        "monthly_issue_data": monthly_issue_data,

                         
        "monthly_return_labels": monthly_return_labels,
        "monthly_return_data": monthly_return_data,

                      
        "monthly_fine_labels": monthly_fine_labels,
        "monthly_fine_data": monthly_fine_data,
        "overdue_labels": overdue_labels,
        "overdue_days": overdue_days,
    }

    return render(
        request,
        "reports.html",
        context
    )


                                                              
                       
                                                              

                                                              
             
                                                              

@login_required
def monthly_report(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Staff access required."
        )
        return redirect("student_dashboard")

                                                                  
                    
                                                                  

    selected_month = request.GET.get(
        "month",
        ""
    ).strip()

                                                                  
            
                                                                  

    issues = (
        Issue.objects
        .select_related(
            "student",
            "book",
        )
        .all()
    )

                                                                  
              
                                                                  

    payments = (
        FinePayment.objects
        .select_related(
            "issue",
            "issue__student",
            "issue__book",
        )
        .all()
    )

                                                                  
                  
                                                                  

    if selected_month:

        try:

            year, month = selected_month.split("-")

            year = int(year)
            month = int(month)

            issues = issues.filter(
                issue_date__year=year,
                issue_date__month=month,
            )

            payments = payments.filter(
                payment_date__year=year,
                payment_date__month=month,
            )

        except (ValueError, TypeError):

            selected_month = ""

                                                                  
                      
                                                                  

    total_issues = issues.count()

    returned_books = issues.filter(
        returned=True
    ).count()

    active_issues = issues.filter(
        returned=False
    ).count()

    late_books = sum(
        issue.late_days
        for issue in issues
    )

                                                                  
                  
                                                                  

    total_fine = issues.aggregate(
        total=Sum("fine")
    )["total"] or 0

    total_collected = payments.aggregate(
        total=Sum("paid_amount")
    )["total"] or 0

    total_outstanding = max(
        total_fine - total_collected,
        0
    )

                                                                  
                         
                                                                  

    monthly_issue_labels = []

    monthly_issue_data = []

    if selected_month:

        monthly_issue_labels = [
            selected_month
        ]

        monthly_issue_data = [
            total_issues
        ]

    else:

        monthly_issue_query = (
            Issue.objects
            .annotate(
                month=TruncMonth("issue_date")
            )
            .values("month")
            .annotate(
                total=Count("id")
            )
            .order_by("month")
        )

        monthly_issue_labels = [
            item["month"].strftime("%b %Y")
            for item in monthly_issue_query
            if item["month"]
        ]

        monthly_issue_data = [
            item["total"]
            for item in monthly_issue_query
            if item["month"]
        ]

                                                                  
                          
                                                                  

    monthly_return_labels = []

    monthly_return_data = []

    if selected_month:

        monthly_return_labels = [
            selected_month
        ]

        monthly_return_data = [
            returned_books
        ]

    else:

        monthly_return_query = (
            Issue.objects
            .filter(
                returned=True,
                return_date__isnull=False
            )
            .annotate(
                month=TruncMonth("return_date")
            )
            .values("month")
            .annotate(
                total=Count("id")
            )
            .order_by("month")
        )

        monthly_return_labels = [
            item["month"].strftime("%b %Y")
            for item in monthly_return_query
            if item["month"]
        ]

        monthly_return_data = [
            item["total"]
            for item in monthly_return_query
            if item["month"]
        ]

                                                                  
                        
                                                                  

    monthly_fine_labels = []

    monthly_fine_data = []

    if selected_month:

        monthly_fine_labels = [
            selected_month
        ]

        monthly_fine_data = [
            total_collected
        ]

    else:

        monthly_payment_query = (
            FinePayment.objects
            .filter(
                payment_date__isnull=False
            )
            .annotate(
                month=TruncMonth("payment_date")
            )
            .values("month")
            .annotate(
                collected=Sum("paid_amount")
            )
            .order_by("month")
        )

        monthly_fine_labels = [
            item["month"].strftime("%b %Y")
            for item in monthly_payment_query
            if item["month"]
        ]

        monthly_fine_data = [
            item["collected"] or 0
            for item in monthly_payment_query
            if item["month"]
        ]

                                                                  
             
                                                                  

    context = {

        "selected_month": selected_month,

                          
        "total_issues": total_issues,

        "returned_books": returned_books,

        "active_issues": active_issues,

        "late_books": late_books,

                      
        "total_fine": total_fine,

        "total_collected": total_collected,

        "total_outstanding": total_outstanding,

                       
        "issues": issues.order_by(
            "-issue_date"
        ),

                             
        "monthly_issue_labels": monthly_issue_labels,

        "monthly_issue_data": monthly_issue_data,

                              
        "monthly_return_labels": monthly_return_labels,

        "monthly_return_data": monthly_return_data,

                            
        "monthly_fine_labels": monthly_fine_labels,

        "monthly_fine_data": monthly_fine_data,
    }

                                                                  
            
                                                                  

    return render(
        request,
        "reports/monthly_report.html",
        context,
    )
                                                            
            
                                                            

@login_required
def issue_report(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Staff access required."
        )
        return redirect("student_dashboard")

    issues = (
        Issue.objects
        .select_related(
            "student",
            "book",
        )
        .all()
        .order_by(
            "-issue_date",
            "-id"
        )
    )

    search = request.GET.get(
        "q",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if search:
        issues = issues.filter(
            Q(
                student__name__icontains=search
            )
            |
            Q(
                student__roll_no__icontains=search
            )
            |
            Q(
                book__title__icontains=search
            )
            |
            Q(
                book__isbn__icontains=search
            )
        )

    if status == "issued":

        issues = issues.filter(
            returned=False
        )

    elif status == "returned":

        issues = issues.filter(
            returned=True
        )

    elif status == "late":

        issues = issues.filter(
            returned=False,
            due_date__lt=timezone.localdate()
        )

    context = {
        "issues": issues,
        "search": search,
        "status": status,
    }

    return render(
        request,
        "reports/issue_report.html",
        context,
    )


                                                              
               
                                                              

@login_required
def return_report(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Staff access required."
        )
        return redirect("student_dashboard")

    issues = (
        Issue.objects
        .select_related(
            "student",
            "book",
        )
        .filter(
            returned=True,
        )
        .order_by(
            "-return_date",
            "-id"
        )
    )

    search = request.GET.get(
        "q",
        ""
    ).strip()

    if search:

        issues = issues.filter(
            Q(
                student__name__icontains=search
            )
            |
            Q(
                student__roll_no__icontains=search
            )
            |
            Q(
                book__title__icontains=search
            )
            |
            Q(
                book__isbn__icontains=search
            )
        )

    context = {
        "issues": issues,
        "search": search,
    }

    return render(
        request,
        "reports/return_report.html",
        context,
    )


                                                              
             
                                                              

@login_required
def fine_report(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Staff access required."
        )
        return redirect("student_dashboard")

    payments = (
        FinePayment.objects
        .select_related(
            "issue",
            "issue__student",
            "issue__book",
        )
        .all()
        .order_by(
            "-created_at"
        )
    )

    search = request.GET.get(
        "q",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if search:

        payments = payments.filter(
            Q(
                issue__student__name__icontains=search
            )
            |
            Q(
                issue__student__roll_no__icontains=search
            )
            |
            Q(
                issue__book__title__icontains=search
            )
            |
            Q(
                issue__book__isbn__icontains=search
            )
            |
            Q(
                transaction_id__icontains=search
            )
        )

    if status in [
        "Pending",
        "Partial",
        "Paid",
    ]:

        payments = payments.filter(
            payment_status=status
        )

    total_fine = sum(
        payment.fine_amount
        for payment in payments
    )

    total_paid = sum(
        payment.paid_amount
        for payment in payments
    )

    total_pending = sum(
        payment.pending_amount
        for payment in payments
    )

    pending_count = payments.filter(
        payment_status="Pending"
    ).count()

    partial_count = payments.filter(
        payment_status="Partial"
    ).count()

    paid_count = payments.filter(
        payment_status="Paid"
    ).count()

    context = {

        "payments": payments,

        "search": search,

        "status": status,

        "total_fine": total_fine,

        "total_paid": total_paid,

        "total_pending": total_pending,

        "pending_count": pending_count,

        "partial_count": partial_count,

        "paid_count": paid_count,
    }

    return render(
        request,
        "reports/fine_report.html",
        context,
    )


                                                              
                
                                                              

                                                              
                
                                                              

@login_required
def student_report(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Staff access required."
        )
        return redirect("student_dashboard")

    students = Student.objects.all().order_by("name")

    search = request.GET.get(
        "q",
        ""
    ).strip()

    if search:
        students = students.filter(
            Q(name__icontains=search)
            |
            Q(roll_no__icontains=search)
            |
            Q(email__icontains=search)
            |
            Q(phone__icontains=search)
        )

    student_reports = []

    for student in students:

        issues = Issue.objects.filter(
            student=student
        ).select_related(
            "book"
        )

        total_issued = issues.count()

        total_returned = issues.filter(
            returned=True
        ).count()

        active_issues = issues.filter(
            returned=False
        ).count()

        overdue_issues = issues.filter(
            returned=False,
            due_date__lt=timezone.localdate()
        ).count()

        total_fine = sum(
            issue.fine
            for issue in issues
        )

        payments = FinePayment.objects.filter(
            issue__student=student
        )

        total_paid = sum(
            payment.paid_amount
            for payment in payments
        )

        total_pending = sum(
            payment.pending_amount
            for payment in payments
        )

        student_reports.append({
            "student": student,
            "total_issued": total_issued,
            "total_returned": total_returned,
            "active_issues": active_issues,
            "overdue_issues": overdue_issues,
            "total_fine": total_fine,
            "total_paid": total_paid,
            "total_pending": total_pending,
        })

    total_students = len(student_reports)

    total_issued = sum(
        item["total_issued"]
        for item in student_reports
    )

    total_returned = sum(
        item["total_returned"]
        for item in student_reports
    )

    total_active = sum(
        item["active_issues"]
        for item in student_reports
    )

    total_overdue = sum(
        item["overdue_issues"]
        for item in student_reports
    )

    total_fine = sum(
        item["total_fine"]
        for item in student_reports
    )

    total_paid = sum(
        item["total_paid"]
        for item in student_reports
    )

    total_pending = sum(
        item["total_pending"]
        for item in student_reports
    )

    context = {
        "student_reports": student_reports,
        "search": search,

        "total_students": total_students,
        "total_issued": total_issued,
        "total_returned": total_returned,
        "total_active": total_active,
        "total_overdue": total_overdue,

        "total_fine": total_fine,
        "total_paid": total_paid,
        "total_pending": total_pending,
    }

    return render(
        request,
        "reports/student_report.html",
        context
    )
                                                              
                       
                                                              

@login_required
def book_inventory_report(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Staff access required."
        )
        return redirect("student_dashboard")

    books = Book.objects.all().order_by("title")

    search = request.GET.get(
        "q",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if search:
        books = books.filter(
            Q(title__icontains=search)
            |
            Q(author__icontains=search)
            |
            Q(isbn__icontains=search)
            |
            Q(category__icontains=search)
        )

    if status == "In Stock":
        books = [
            book for book in books
            if book.inventory_status == "In Stock"
        ]

    elif status == "Low Stock":
        books = [
            book for book in books
            if book.inventory_status == "Low Stock"
        ]

    elif status == "Out of Stock":
        books = [
            book for book in books
            if book.inventory_status == "Out of Stock"
        ]

    total_books = len(books)

    total_copies = sum(
        book.quantity
        for book in books
    )

    issued_copies = sum(
        book.issued_quantity
        for book in books
    )

    available_copies = sum(
        book.available_quantity
        for book in books
    )

    low_stock_books = sum(
        1
        for book in books
        if book.inventory_status == "Low Stock"
    )

    out_of_stock_books = sum(
        1
        for book in books
        if book.inventory_status == "Out of Stock"
    )

    context = {
        "books": books,
        "search": search,
        "status": status,

        "total_books": total_books,
        "total_copies": total_copies,
        "issued_copies": issued_copies,
        "available_copies": available_copies,
        "low_stock_books": low_stock_books,
        "out_of_stock_books": out_of_stock_books,
    }

    return render(
        request,
        "reports/book_inventory_report.html",
        context
    )
@login_required
def export_csv(request):

    if not request.user.is_staff:
        messages.error(request, "Staff access required.")
        return redirect("student_dashboard")

    report_type = request.GET.get("type", "issues").strip()

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{report_type}_report.csv"'
    )

    writer = csv.writer(response)

                               
                  
                               

    if report_type == "issues":

        writer.writerow([
            "Student Name",
            "Roll Number",
            "Book Title",
            "ISBN",
            "Issue Date",
            "Due Date",
            "Return Date",
            "Status",
            "Fine"
        ])

        issues = Issue.objects.select_related(
            "student",
            "book"
        ).order_by("-issue_date")

        for issue in issues:

            writer.writerow([
                issue.student.name,
                issue.student.roll_no,
                issue.book.title,
                issue.book.isbn,
                issue.issue_date,
                issue.due_date,
                issue.return_date or "",
                issue.status,
                issue.fine
            ])

                               
                    
                               

    elif report_type == "students":

        writer.writerow([
            "Student Name",
            "Roll Number",
            "Email",
            "Phone",
            "Total Issued",
            "Total Returned",
            "Currently Issued",
            "Overdue Books",
            "Total Fine",
            "Fine Paid",
            "Outstanding Fine"
        ])

        students = Student.objects.all().order_by("name")

        for student in students:

            issues = Issue.objects.filter(
                student=student
            )

            total_issued = issues.count()

            total_returned = issues.filter(
                returned=True
            ).count()

            active_issues = issues.filter(
                returned=False
            ).count()

            overdue_issues = issues.filter(
                returned=False,
                due_date__lt=timezone.localdate()
            ).count()

            total_fine = sum(
                issue.fine
                for issue in issues
            )

            payments = FinePayment.objects.filter(
                issue__student=student
            )

            total_paid = sum(
                payment.paid_amount
                for payment in payments
            )

            total_pending = sum(
                payment.pending_amount
                for payment in payments
            )

            writer.writerow([
                student.name,
                student.roll_no,
                student.email,
                student.phone,
                total_issued,
                total_returned,
                active_issues,
                overdue_issues,
                total_fine,
                total_paid,
                total_pending
            ])

                               
                 
                               

    elif report_type == "fines":

        writer.writerow([
            "Student Name",
            "Roll Number",
            "Book Title",
            "Fine Amount",
            "Paid Amount",
            "Pending Amount",
            "Payment Status",
            "Payment Method",
            "Payment Date",
            "Transaction ID"
        ])

        payments = FinePayment.objects.select_related(
            "issue",
            "issue__student",
            "issue__book"
        ).order_by("-created_at")

        for payment in payments:

            writer.writerow([
                payment.issue.student.name,
                payment.issue.student.roll_no,
                payment.issue.book.title,
                payment.fine_amount,
                payment.paid_amount,
                payment.pending_amount,
                payment.payment_status,
                payment.payment_method,
                payment.payment_date or "",
                payment.transaction_id
            ])

                               
                           
                               

    elif report_type == "inventory":

        writer.writerow([
            "Book Title",
            "Author",
            "ISBN",
            "Category",
            "Total Quantity",
            "Issued Copies",
            "Available Copies",
            "Issue Percentage",
            "Stock Status",
            "Shelf Number",
            "Rack Number"
        ])

        books = Book.objects.all().order_by("title")

        for book in books:

            writer.writerow([
                book.title,
                book.author,
                book.isbn,
                book.category,
                book.quantity,
                book.issued_quantity,
                book.available_quantity,
                f"{book.issue_percentage}%",
                book.inventory_status,
                book.shelf_number,
                book.rack_number
            ])

                               
                   
                               

    elif report_type == "returns":

        writer.writerow([
            "Student Name",
            "Roll Number",
            "Book Title",
            "Issue Date",
            "Due Date",
            "Return Date",
            "Late Days",
            "Fine"
        ])

        issues = Issue.objects.select_related(
            "student",
            "book"
        ).filter(
            returned=True
        ).order_by("-return_date")

        for issue in issues:

            writer.writerow([
                issue.student.name,
                issue.student.roll_no,
                issue.book.title,
                issue.issue_date,
                issue.due_date,
                issue.return_date,
                issue.late_days,
                issue.fine
            ])

    else:

        writer.writerow([
            "Error"
        ])

        writer.writerow([
            "Invalid report type"
        ])

    return response
@login_required
def export_pdf(request):

    if not request.user.is_staff:
        messages.error(request, "Staff access required.")
        return redirect("student_dashboard")

    report_type = request.GET.get(
        "type",
        "issues"
    ).strip()

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    normal_style = styles["Normal"]

    elements = []

    title_map = {
        "issues": "Library Issue Report",
        "returns": "Library Return Report",
        "fines": "Library Fine Report",
        "students": "Library Student Report",
        "inventory": "Library Book Inventory Report",
    }

    title = title_map.get(
        report_type,
        "Library Report"
    )

    elements.append(
        Paragraph(
            title,
            title_style
        )
    )

    elements.append(
        Spacer(1, 15)
    )

                               
                  
                               

    if report_type == "issues":

        data = [
            [
                "Student",
                "Roll No",
                "Book",
                "ISBN",
                "Issue Date",
                "Due Date",
                "Return Date",
                "Status",
                "Fine",
            ]
        ]

        issues = Issue.objects.select_related(
            "student",
            "book"
        ).order_by("-issue_date")

        for issue in issues:

            data.append([
                issue.student.name,
                issue.student.roll_no,
                issue.book.title,
                issue.book.isbn,
                str(issue.issue_date),
                str(issue.due_date),
                str(issue.return_date)
                if issue.return_date
                else "-",
                issue.status,
                f"₹{issue.fine}",
            ])

                               
                   
                               

    elif report_type == "returns":

        data = [
            [
                "Student",
                "Roll No",
                "Book",
                "Issue Date",
                "Due Date",
                "Return Date",
                "Late Days",
                "Fine",
            ]
        ]

        issues = Issue.objects.select_related(
            "student",
            "book"
        ).filter(
            returned=True
        ).order_by("-return_date")

        for issue in issues:

            data.append([
                issue.student.name,
                issue.student.roll_no,
                issue.book.title,
                str(issue.issue_date),
                str(issue.due_date),
                str(issue.return_date),
                issue.late_days,
                f"₹{issue.fine}",
            ])

                               
                 
                               

    elif report_type == "fines":

        data = [
            [
                "Student",
                "Roll No",
                "Book",
                "Fine",
                "Paid",
                "Pending",
                "Status",
                "Method",
                "Payment Date",
                "Transaction ID",
            ]
        ]

        payments = FinePayment.objects.select_related(
            "issue",
            "issue__student",
            "issue__book"
        ).order_by("-created_at")

        for payment in payments:

            data.append([
                payment.issue.student.name,
                payment.issue.student.roll_no,
                payment.issue.book.title,
                f"₹{payment.fine_amount}",
                f"₹{payment.paid_amount}",
                f"₹{payment.pending_amount}",
                payment.payment_status,
                payment.payment_method or "-",
                str(payment.payment_date)
                if payment.payment_date
                else "-",
                payment.transaction_id or "-",
            ])

                               
                    
                               

    elif report_type == "students":

        data = [
            [
                "Student",
                "Roll No",
                "Email",
                "Phone",
                "Issued",
                "Returned",
                "Active",
                "Overdue",
                "Fine",
                "Paid",
                "Outstanding",
            ]
        ]

        students = Student.objects.all().order_by("name")

        for student in students:

            issues = Issue.objects.filter(
                student=student
            )

            total_issued = issues.count()

            total_returned = issues.filter(
                returned=True
            ).count()

            active_issues = issues.filter(
                returned=False
            ).count()

            overdue_issues = issues.filter(
                returned=False,
                due_date__lt=timezone.localdate()
            ).count()

            total_fine = sum(
                issue.fine
                for issue in issues
            )

            payments = FinePayment.objects.filter(
                issue__student=student
            )

            total_paid = sum(
                payment.paid_amount
                for payment in payments
            )

            total_pending = sum(
                payment.pending_amount
                for payment in payments
            )

            data.append([
                student.name,
                student.roll_no,
                student.email,
                student.phone,
                total_issued,
                total_returned,
                active_issues,
                overdue_issues,
                f"₹{total_fine}",
                f"₹{total_paid}",
                f"₹{total_pending}",
            ])

                               
                      
                               

    elif report_type == "inventory":

        data = [
            [
                "Book",
                "Author",
                "ISBN",
                "Category",
                "Quantity",
                "Issued",
                "Available",
                "Issue %",
                "Status",
                "Shelf",
                "Rack",
            ]
        ]

        books = Book.objects.all().order_by("title")

        for book in books:

            data.append([
                book.title,
                book.author,
                book.isbn,
                book.category,
                book.quantity,
                book.issued_quantity,
                book.available_quantity,
                f"{book.issue_percentage}%",
                book.inventory_status,
                book.shelf_number or "-",
                book.rack_number or "-",
            ])

    else:

        data = [
            ["Error"],
            ["Invalid report type"],
        ]

                               
                  
                               

    table = Table(
        data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1f2937"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#f3f4f6"),
                ],
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
        ])
    )

    elements.append(table)

    pdf.build(elements)

    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{report_type}_report.pdf"'
    )

    return response
                                                                  
                      
                                                                  

    top_books = (
        Book.objects
        .annotate(
            issue_count=Count("issue")
        )
        .order_by(
            "-issue_count",
            "title"
        )[:5]
    )

    top_books_labels = [
        book.title
        for book in top_books
    ]

    top_books_data = [
        book.issue_count
        for book in top_books
    ]


                                                                  
                         
                                                                  

    top_students = (
        Student.objects
        .annotate(
            issue_count=Count("issue")
        )
        .order_by(
            "-issue_count",
            "name"
        )[:5]
    )

    top_students_labels = [
        student.name
        for student in top_students
    ]

    top_students_data = [
        student.issue_count
        for student in top_students
    ]


                                                                  
                           
                                                                  

    category_data = {}

    for book in books:

        category = book.category or "General"

        category_data[category] = (
            category_data.get(category, 0)
            + book.quantity
        )

    category_labels = list(
        category_data.keys()
    )

    category_values = list(
        category_data.values()
    )


                                                                  
                    
                                                                  

    paid_payments = FinePayment.objects.filter(
        payment_status="Paid"
    ).count()

    partial_payments = FinePayment.objects.filter(
        payment_status="Partial"
    ).count()

    pending_payments = FinePayment.objects.filter(
        payment_status="Pending"
    ).count()

    payment_status_labels = [
        "Paid",
        "Partial",
        "Pending",
    ]

    payment_status_data = [
        paid_payments,
        partial_payments,
        pending_payments,
    ]
                     
                                                              

def notifications(request):

    if not request.user.is_staff:

        messages.error(
            request,
            "Staff access required."
        )

        return redirect(
            "student_dashboard"
        )

    generate_notifications()

    notification_list = Notification.objects.all().order_by(
        "-is_read",
        "-created_at"
    )

    unread_count = Notification.objects.filter(
        is_read=False
    ).count()

    context = {
        "notifications": notification_list,
        "unread_count": unread_count,
    }

    return render(
        request,
        "notifications/notifications.html",
        context
    )


                                                              
                                  
                                                              

@login_required
def mark_notification_read(
    request,
    notification_id
):

    if not request.user.is_staff:

        messages.error(
            request,
            "Staff access required."
        )

        return redirect(
            "student_dashboard"
        )

    notification = get_object_or_404(
        Notification,
        id=notification_id
    )

    notification.is_read = True

    notification.save(
        update_fields=[
            "is_read"
        ]
    )

    return redirect(
        "notifications"
    )


                                                              
                                
                                                              

@login_required
def mark_all_notifications_read(request):

    if not request.user.is_staff:

        messages.error(
            request,
            "Staff access required."
        )

        return redirect(
            "student_dashboard"
        )

    Notification.objects.filter(
        is_read=False
    ).update(
        is_read=True
    )

    return redirect(
        "notifications"
    )
                                                              
                                   
                                                              

def generate_notifications():

    today = timezone.localdate()
    valid_notifications = set()

                                                              
                   
                                                              

    overdue_issues = Issue.objects.select_related(
        "student", "book"
    ).filter(
        returned=False,
        due_date__lt=today
    )

    for issue in overdue_issues:
        late_days = (today - issue.due_date).days
        title = f"Overdue Book: {issue.book.title}"
        message = (
            f"{issue.student.name} has not returned "
            f"'{issue.book.title}'. "
            f"The book is {late_days} day(s) overdue."
        )
        valid_notifications.add((title, "overdue"))
        notification, created = Notification.objects.get_or_create(
            title=title,
            notification_type="overdue",
            defaults={"message": message}
        )
        if not created and notification.message != message:
            notification.message = message
            notification.save(update_fields=["message"])

                                                              
                    
                                                              

    due_soon_date = today + timedelta(days=2)
    due_soon_issues = Issue.objects.select_related(
        "student", "book"
    ).filter(
        returned=False,
        due_date__gte=today,
        due_date__lte=due_soon_date
    )

    for issue in due_soon_issues:
        remaining_days = (issue.due_date - today).days
        title = f"Book Due Soon: {issue.book.title}"
        message = (
            f"{issue.student.name} must return "
            f"'{issue.book.title}' within "
            f"{remaining_days} day(s)."
        )
        valid_notifications.add((title, "due_soon"))
        notification, created = Notification.objects.get_or_create(
            title=title,
            notification_type="due_soon",
            defaults={"message": message}
        )
        if not created and notification.message != message:
            notification.message = message
            notification.save(update_fields=["message"])

                                                              
                    
                                                              

    for book in Book.objects.all():
        if 0 < book.available_quantity <= 2:
            title = f"Low Stock: {book.title}"
            message = (
                f"'{book.title}' has only "
                f"{book.available_quantity} copy/copies available."
            )
            notification_type = "low_stock"
        elif book.available_quantity <= 0:
            title = f"Out of Stock: {book.title}"
            message = (
                f"All copies of '{book.title}' "
                f"are currently issued."
            )
            notification_type = "out_of_stock"
        else:
            continue

        valid_notifications.add((title, notification_type))
        notification, created = Notification.objects.get_or_create(
            title=title,
            notification_type=notification_type,
            defaults={"message": message}
        )
        if not created and notification.message != message:
            notification.message = message
            notification.save(update_fields=["message"])

                                                              
                   
                                                              

    payments = FinePayment.objects.select_related(
        "issue", "issue__student", "issue__book"
    ).filter(
        paid_amount__lt=F("fine_amount")
    )

    for payment in payments:
        pending_amount = payment.fine_amount - payment.paid_amount
        title = f"Pending Fine: {payment.issue.student.name}"
        message = (
            f"{payment.issue.student.name} has "
            f"₹{pending_amount} pending fine "
            f"for '{payment.issue.book.title}'."
        )
        valid_notifications.add((title, "fine"))
        notification, created = Notification.objects.get_or_create(
            title=title,
            notification_type="fine",
            defaults={"message": message}
        )
        if not created and notification.message != message:
            notification.message = message
            notification.save(update_fields=["message"])

                                                              
                                
                                                              

    notification_types = [
        "overdue",
        "due_soon",
        "low_stock",
        "out_of_stock",
        "fine",
    ]

    for notification in Notification.objects.filter(
        notification_type__in=notification_types
    ):
        key = (notification.title, notification.notification_type)
        if key not in valid_notifications:
            notification.delete()
