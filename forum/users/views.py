from django.shortcuts import render, HttpResponse

import logging

logger = logging.getLogger(__name__)

# Create your views here.

def users(request):
    try:
        logger.info("Processing the request.")
        return HttpResponse("Not implemented")
    except Exception as e:
        logger.error(f"Error occurred: {e}")

