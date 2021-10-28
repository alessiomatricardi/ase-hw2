from flask import render_template

class ErrorDetail:
    def __init__(self, errorCode):
        self.code = errorCode
        if errorCode == 401:
            self.name = 'Error 401 - Unauthorized'
            self.description = 'You must login to see this content'
        elif errorCode == 403:
            self.name = 'Error 403 - Forbidden'
            self.description = 'You haven\'t access to this resource'
        elif errorCode == 404:
            self.name = 'Error 404 - Not found'
            self.description = 'The resource you\'re searching for doesn\'t exists'
        else:
            self.name = 'Error ' + errorCode
            self.description = 'Something went wrong'


# User must login to see the content of the page
# TODO TBD if necessary
def unauthorized(e):
    error = ErrorDetail(401)
    return render_template('error.html', error = error), 401

# The content is not available for the user
def forbidden(e):
    error = ErrorDetail(403)
    return render_template('error.html', error = error), 403

# The page simply doesn't exist
def page_not_found(e):
    error = ErrorDetail(404)
    return render_template('error.html', error = error), 404
