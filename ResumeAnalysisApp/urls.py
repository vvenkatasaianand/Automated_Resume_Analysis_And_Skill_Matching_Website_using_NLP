from django.urls import path

from . import views

urlpatterns = [path("", views.index, name="home"),
    	#    path("index.html", views.index, name="index"),
	       path('AdminLogin.html', views.AdminLogin, name="AdminLogin"), 
	       path('AdminLoginAction.html', views.AdminLoginAction, name="AdminLoginAction"),
	       path('UserLogin', views.UserLogin, name="UserLogin"),
	       path('UserLoginAction', views.UserLoginAction, name="UserLoginAction"),	   
	       path('Signup', views.Signup, name="Signup"),
	       path('SignupAction', views.SignupAction, name="SignupAction"),
	       path('PostJobs', views.PostJobs, name="PostJobs"),
	       path('PostJobsAction', views.PostJobsAction, name="PostJobsAction"),
	       path('ViewScore', views.ViewScore, name="ViewScore"),
	       path('Feedback', views.Feedback, name="Feedback"),
	       path('FeedbackAction', views.FeedbackAction, name="FeedbackAction"),	
	       path('Aboutus', views.Aboutus, name="Aboutus"),
	       path('ViewFeedback', views.ViewFeedback, name="ViewFeedback"),
	       path('ViewJobs', views.ViewJobs, name="ViewJobs"),
	       path('AllViewScore', views.AllViewScore, name="AllViewScore"),
	       path('UploadResume', views.UploadResume, name="UploadResume"),
	       path('UploadResumeAction', views.UploadResumeAction, name="UploadResumeAction"),	   
	       path('ViewScore', views.ViewScore, name="ViewScore"),
	       path('UserDashboard', views.UserDashboard, name="UserDashboard"),
	       path('AdminDashboard', views.AdminDashboard, name="AdminDashboard"),
	       path('DeleteJobAction', views.DeleteJobAction, name="DeleteJobAction"),
	       path('MakeSelected', views.MakeSelected, name="MakeSelected"),
	       path('MakeRejected', views.MakeRejected, name="MakeRejected"),
           path('editjobs/<int:job_id>/', views.EditJobs, name='EditJobs'),
	       path('EditJobsAction/<int:job_id>/', views.EditJobsAction, name="EditJobsAction"),
           
]