import datetime
import os

from flask import Blueprint, config, redirect, render_template, request, json, current_app, abort
from flask.helpers import flash, send_from_directory, url_for
from flask.signals import message_flashed, request_finished
from sqlalchemy.orm import query
from sqlalchemy.sql.elements import Null
from werkzeug.utils import secure_filename
from monolith.message_logic import MessageLogic
from monolith.database import Message, Message_Recipient, User, db
from monolith.forms import MessageForm
from monolith.auth import current_user

#