from django.urls import path
from job import views

urlpatterns = [
    path('',views.load_home, name='load_home'),
    path('post/job/',views.post_job, name='post_job'),
    path('job/<slug>/',views.job_detail, name='job_detail'),
    path('apply/<slug>/', views.apply_job, name='apply_job'),
    path('job/edit/<slug>/',views.edit_job, name='edit_job'),
    path('job/applicants/<slug>/', views.see_applicants, name='see_applicants'),

]