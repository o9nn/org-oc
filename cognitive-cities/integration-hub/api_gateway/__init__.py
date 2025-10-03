"""
API Gateway Package - Integration Hub

RESTful API gateway for unified access to cognitive triads.
"""

from .api_gateway import CognitiveAPIGateway, create_api_gateway

__all__ = ['CognitiveAPIGateway', 'create_api_gateway']