from rest_framework.renderers import JSONRenderer
from rest_framework.status import is_client_error, is_server_error


class ClickUpResponeRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]

        modified_data = {}
        modified_data["statusCode"] = response.status_code
        modified_data["success"] = not self.is_error(response.status_code)

        if isinstance(data, dict):
            if data.get("message"):
                modified_data["message"] = data.pop("message")

            if data:
                if self.is_error(response.status_code):
                    modified_data["errors"] = data.get("errors") or data
                else:
                    if data.get("allocatedUsers"):
                        modified_data["allocatedUsers"] = data.get("allocatedUsers")
                    elif data.get("ticketData") is not None:
                        modified_data.update(data)
                    else:
                        modified_data["data"] = data.get("data") or data
        else:
            if self.is_error(response.status_code):
                modified_data["errors"] = data
            else:
                modified_data["data"] = data

        return super().render(modified_data, accepted_media_type, renderer_context)

    def is_error(self, status_code):
        return is_client_error(status_code) or is_server_error(status_code)
