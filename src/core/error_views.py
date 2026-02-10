from django.shortcuts import render


def handler404(request, *args, **argv):
    template = "404.html"
    context = {}
    return render(
        request=request,
        template_name=template,
        context=context,
        status=404,
    )


def handler500(request, *args, **argv):
    response = render(
        request=request,
        template_name='500.html',
        status=500,

    )
    return response
