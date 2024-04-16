import os
import requests
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from django.conf import settings

from clickup_auth.models import ClickUpUser
from clickup_projects.models import Employee


# Create your views here.
@api_view(["POST"])
def google_auth_callback(request):

    if request.method == "POST":
        if "idToken" in request.data:
            userinfo_response = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={
                    "Authorization": f"Bearer {request.data['idToken']}",
                },
            )
            userinfo_data = userinfo_response.json()

            try:
                clickup_user = ClickUpUser.objects.get(email=userinfo_data.get("email"))
            except ClickUpUser.DoesNotExist:
                return Response("User Not found", HTTP_400_BAD_REQUEST)

            clickup_user.first_name = userinfo_data.get("given_name")
            clickup_user.last_name = userinfo_data.get("family_name")
            clickup_user.save()

            employee = Employee.objects.get_or_create(user=clickup_user)[0]
            if userinfo_data.get("picture"):
                response = requests.get(userinfo_data.get("picture"))
                response.raise_for_status()

                save_directory = f"employee/{employee._id}/"
                os.makedirs(
                    os.path.join(settings.MEDIA_ROOT, save_directory), exist_ok=True
                )
                photo_path = f"{employee._id}_photo.jpg"
                with open(
                    os.path.join(settings.MEDIA_ROOT, save_directory, photo_path), "wb"
                ) as photo:
                    photo.write(response.content)
                    employee.photo.name = save_directory + photo_path
                    employee.save()

            token = RefreshToken.for_user(user=clickup_user)

            return Response(
                {
                    "data": {
                        "_id": employee._id,
                        "employeeName": employee.user.get_full_name(),
                        "employeeId": employee.employeeId,
                        "photo": employee.photo.url,
                        "email": employee.user.email,
                        "accessToken": str(token.access_token), 
                    },
                    "message": "Login successfully",
                },
                HTTP_200_OK,
            )

        else:
            return Response("idToken Field required", HTTP_400_BAD_REQUEST)
