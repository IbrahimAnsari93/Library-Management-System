from django.urls import path
from . import views


urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "student-dashboard/",
        views.student_dashboard,
        name="student_dashboard",
    ),

    path(
        "students/",
        views.student_list,
        name="student_list",
    ),

    path(
        "students/add/",
        views.student_add,
        name="student_add",
    ),

    path(
        "students/<int:id>/",
        views.student_detail,
        name="student_detail",
    ),

    path(
        "students/edit/<int:id>/",
        views.student_edit,
        name="student_edit",
    ),

    path(
        "students/delete/<int:id>/",
        views.student_delete,
        name="student_delete",
    ),

    path(
        "books/",
        views.book_list,
        name="book_list",
    ),

    path(
        "books/add/",
        views.add_book,
        name="add_book",
    ),

    path(
        "books/<int:id>/",
        views.book_detail,
        name="book_detail",
    ),

    path(
        "books/edit/<int:id>/",
        views.edit_book,
        name="edit_book",
    ),

    path(
        "books/delete/<int:id>/",
        views.delete_book,
        name="delete_book",
    ),

    path(
        "issue/",
        views.issue_book,
        name="issue_book",
    ),

    path(
        "issues/",
        views.issue_list,
        name="issue_list",
    ),

    path(
        "return/<int:id>/",
        views.return_book,
        name="return_book",
    ),

    path(
        "inventory/",
        views.inventory_dashboard,
        name="inventory_dashboard",
    ),

    path(
        "fine-management/",
        views.fine_management,
        name="fine_management",
    ),

    path(
        "pay-fine/<int:id>/",
        views.pay_fine,
        name="pay_fine",
    ),

    path(
        "fine-receipt/<int:id>/",
        views.fine_receipt,
        name="fine_receipt",
    ),

    path(
        "payment-history/",
        views.payment_history,
        name="payment_history",
    ),

    path(
        "reports/",
        views.reports,
        name="reports",
    ),

    path(
        "reports/monthly/",
        views.monthly_report,
        name="monthly_report",
    ),

    path(
        "reports/issues/",
        views.issue_report,
        name="issue_report",
    ),

    path(
        "reports/returns/",
        views.return_report,
        name="return_report",
    ),

    path(
        "reports/fines/",
        views.fine_report,
        name="fine_report",
    ),

    path(
        "reports/students/",
        views.student_report,
        name="student_report",
    ),

    path(
        "reports/inventory/",
        views.book_inventory_report,
        name="book_inventory_report",
    ),

                
    path(
        "reports/export/",
        views.export_csv,
        name="export_csv",
    ),

                
    path(
        "reports/export/pdf/",
        views.export_pdf,
        name="export_pdf",
    ),

    path(
        "notifications/",
        views.notifications,
        name="notifications",
    ),

    path(
        "notifications/read/<int:notification_id>/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),

    path(
        "notifications/read-all/",
        views.mark_all_notifications_read,
        name="mark_all_notifications_read",
    ),
]
