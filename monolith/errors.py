from flask import render_template

class ErrorDetail:
    def __init__(self, errorCode, error_obj):
        self.code = errorCode
        self.customDescription = error_obj.description
        if errorCode == 400:
            self.name = 'Bad request'
            self.description = 'Apparentely you done something wrong... we keep an eye on you'
        if errorCode == 401:
            self.name = 'Unauthorized'
            self.description = 'You must login to see this content'
        elif errorCode == 403:
            self.name = 'Forbidden'
            self.description = 'You haven\'t access to this resource'
        elif errorCode == 404:
            self.name = 'Not found'
            self.description = 'The resource you\'re searching for doesn\'t exists'
        elif errorCode == 405:
            self.name = 'Method not Allowed'
            self.description = 'This resource doesn\'t allow this request method'
        elif errorCode == 409:
            self.name = 'Conflict'
            self.description = 'This resource already exists'
        elif errorCode == 500:
            self.name = 'Internal Server Error'
            self.description = 'Awesome! You broke something... go back and forget this mess'
        else:
            self.name = 'Error ' + str(errorCode)
            self.description = 'Something went wrong'


# User must login to see the content of the page
def bad_request(e):
    error = ErrorDetail(400, e)
    return render_template('error.html', error=error), 400

# User must login to see the content of the page
def unauthorized(e):
    error = ErrorDetail(401, e)
    return render_template('error.html', error = error), 401

# The content is not available for the user
def forbidden(e):
    error = ErrorDetail(403, e)
    return render_template('error.html', error = error), 403

# The page simply doesn't exist
def page_not_found(e):
    error = ErrorDetail(404, e)
    return render_template('error.html', error = error), 404

# This page doesn't allow this request method
def method_not_allowed(e):
    error = ErrorDetail(405, e)
    return render_template('error.html', error = error), 405

# The resource already exist
def conflict(e):
    error = ErrorDetail(409, e)
    return render_template('error.html', error = error), 409

# Internal server error, usually occours when something fails
def internal_server(e):
    error = ErrorDetail(500, e)
    return render_template('error.html', error = error), 500