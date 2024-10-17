from django.urls import path
from .views import (consulting, consusers, conscharai, consteammembership, consservices, consconversation, \
                    conscontactmessage,telegrammessage,
                    consblogpost, conschatfile, conschatrequests,conshistory
    # consservicemembership
                    )

urlpatterns = [
    path('consulting/', consulting, name='consulting'),
    path('consusers/',consusers,name='consusers'),
    path('conscharai/',conscharai,name='conscharai'),
    path('conschatrequests/',conschatrequests,name='conschatrequests'),
    path('consteammemberships/',consteammembership,name='consteammemberships'),
    path('consservices/',consservices,name='consservices'),
    path('consconversation/',consconversation,name='consconversation'),
    path('conscontactmessages/',conscontactmessage,name='conscontactmessages'),
    path('conscomments/',conscontactmessage,name='conscomments'),
    path('consblogposts/',consblogpost,name='consblogposts'),
    path('conschatfile/',conschatfile,name='conschatfile'),
    path('conshistory/',conshistory,name='conshistory'),
    path('constelegram/',telegrammessage,name='constelegram'),

    # path('consservicememberships/',consservicemembership,name='consservicememberships'),
]
