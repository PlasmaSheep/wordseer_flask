from flask import render_template, request

from app import app
from ..models import session, Unit, Project
from .. import forms

PROJECT_ROUTE = "/projects/"

@app.route(PROJECT_ROUTE, methods=["GET", "POST"])
def projects():
    """
    This controller handles projects. It includes a form at the top to
    create a new project, and under the form the page has a listing of
    already created projects owned by the user.
    """
    form = forms.ProjectCreateForm()

    if request.method == "POST" and form.validate():
        #TODO: is this secure? maybe not
        project = Project(name=form.name.data)
        project.save()

    projects = Project.all().all()

    return render_template("projects.html", form=form, projects=projects)

@app.route(PROJECT_ROUTE + "<proj_id>")
def project_show(proj_id):
    """
    Show the files contained in a specific project.

    :param int proj_id: The ID of the desired project.
    """
    files = session.query(Unit).filter(Unit.project == proj_id).\
        filter(Unit.path != None).all()

    project = session.query(Project).filter(Project.id == proj_id).one()

    return render_template("document_index.html", files=files, project=project)