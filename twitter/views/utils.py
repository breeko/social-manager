from django.http import JsonResponse

def say_hi(request):
  name = request.GET.get('name', None)
  data = {
      'out': f"hello {name}"
  }
  return JsonResponse(data)
