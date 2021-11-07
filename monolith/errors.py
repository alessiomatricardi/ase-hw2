from flask import render_template

class ErrorDetail:
    def __init__(self, errorCode, customDescription):
        self.code = errorCode
        self.customDescription = customDescription
        if errorCode == 401:
            self.name = 'Unauthorized'
            self.description = 'You must login to see this content'
        elif errorCode == 403:
            self.name = 'Forbidden'
            self.description = 'You haven\'t access to this resource'
        elif errorCode == 404:
            self.name = 'Not found'
            self.description = 'The resource you\'re searching for doesn\'t exists'
        elif errorCode == 409:
            self.name = 'Conflict'
            self.description = 'This resource already exists'
        elif errorCode == 500:
            self.name = 'Internal Server Error'
            self.description = 'Awesome! You broke something... go back and forget this mess'
        else:
            self.name = 'Error ' + errorCode
            self.description = 'Something went wrong'


# User must login to see the content of the page
# TODO TBD if necessary
def unauthorized(e):
    error = ErrorDetail(401, e.description)
    return render_template('error.html', error = error), 401

# The content is not available for the user
def forbidden(e):
    error = ErrorDetail(403, e.description)
    return render_template('error.html', error = error), 403

# The page simply doesn't exist
def page_not_found(e):
    error = ErrorDetail(404, e.description)
    return render_template('error.html', error = error), 404

# The resource already exist
def conflict(e):
    error = ErrorDetail(409, e.description)
    return render_template('error.html', error = error), 409

# Internal server error, usually occours when something fails
def internal_server(e):
    error = ErrorDetail(500, e.description)
    return render_template('error.html', error = error), 500