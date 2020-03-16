from flask import Flask, render_template, request
from flask_classy import FlaskView
from ..model.project import Provided, Solicited

class SelectedProjectView(FlaskView):
    def get(self):
        #whether the project is provided. Booleans are broken due to a bug within Flask, so we have
        #to use an integer instead. Instead of true and false, we'll use truthy and falsy values
        #e.g., 0=False, >1 = True
        is_provided =  request.args.get('is_provided', default=0, type=int)

        # Get project by id 
        id         =  request.args.get('id', default = ' ', type=int)
        
        if is_provided:
            s = Provided.get(id)
        else:
            s = Solicited.get(id)
            
        # Render HTML
        return render_template('project.html', project = s)
    