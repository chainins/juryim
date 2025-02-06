from django.urls import path, include

urlpatterns = [
    # ... existing urls ...
    path('management/gambling/', 
         include('gambling.urls.management', 
                namespace='gambling_management')),
    path('management/financial/', 
         include('financial.urls.management', 
                namespace='financial_management')),
] 