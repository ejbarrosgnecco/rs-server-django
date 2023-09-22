import json

class JsonRequestMiddleware:
    def __init__ (self, get_response):
        self.get_response = get_response

    def __call__ (self, request):
        if request.content_type == "application/json":
            try:
                request.json_body = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                request.json_body = {}
                pass

        else:
            pass

        response = self.get_response(request)
        return response