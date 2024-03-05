from json import JSONDecodeError
from django.http import JsonResponse
from .serializers import ContactSerializer
from rest_framework.parsers import JSONParser
from rest_framework import views, status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from spyne.server.wsgi import WsgiApplication
from spyne import Application
from .soap_services import HelloWorldService
from spyne.protocol.soap import Soap11
from io import BytesIO
from django.http import HttpResponse, JsonResponse

from django.views.decorators.http import require_http_methods
import hmac
import hashlib


class ContactAPIView(views.APIView):
    """
    A simple APIView for creating contact entires.
    """
    serializer_class = ContactSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = ContactSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)


application = Application([HelloWorldService], tns='django.soap.example', in_protocol=Soap11(validator='lxml'), out_protocol=Soap11())
soap_app = WsgiApplication(application)

@csrf_exempt
def soap_view(request):
    if request.method == 'POST':
        body = request.body
        environ = request.META.copy()
        environ['wsgi.input'] = BytesIO(body)
        environ['CONTENT_LENGTH'] = len(body)
        
        status_code = [None]
        headers_set = []
        def start_response(status, headers):
            status_code[0] = int(status.split()[0])
            headers_set[:] = [(k, v) for k, v in headers]
        
        response_content = soap_app(environ, start_response)
        
        response = HttpResponse(response_content, status=status_code[0])
        for k, v in headers_set:
            response[k] = v
        return response
    else:
        raise Http404
    

@csrf_exempt
@require_http_methods(["POST"])
def webhook(request):
    secret = b"tu_secreto_compartido"
    request_signature = request.headers.get('X-Signature')

    if request_signature and verify_signature(request.body, request_signature, secret):
        return HttpResponse('Webhook procesado correctamente', status=200)
    else:
        return HttpResponse('Firma inválida', status=403)

def verify_signature(body, signature, secret):
    """Verifica la firma HMAC de la solicitud."""
    hmac_digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(hmac_digest, signature)