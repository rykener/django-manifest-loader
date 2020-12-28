# The two ways to build a front end

There are two fundamental ways to connect a javascript front end to Django: coupled or decoupled. Django Manifest loader is specifically for the coupled option. 

A coupled front end and back end means that Django is responsible for the front ends asset files. As a user you point your web browser to the Django app, and the Django app in turn makes sure you get the front end. 

A decoupled front and back end means they are hosted separately. Django has no knowledge of front end asset files, and does not serve them. As a user you point your browser at the staticly hosted front end app and that app interacts with Django through an API. 

I typically choose the coupled option as 
* I don't want to manage multiple repos
* or multiple servers
* Django is powerful

The decoupled option is good for if
* you value the performance gain of using a static file server
* your front end and django app are managed by different teams 
* you want micro services

It's a tradeoff. Django Manifest Loader makes the coupled option much easier than it was before. 