```

# RECIPE APP API

![](https://github.com/Benji918/recepie-app-api/blob/main/readme%20files/recipe%20endpoints.jpeg)
![](https://github.com/Benji918/recepie-app-api/blob/main/readme%20files/img.png)

[PLACE_TO_ADD_LINK_FOR_DEPLOYED_VERSION]

RECIPE APP API is a Django rest api web application that enables users to do the following: -

- Create authenticated users
- Perform CRUD operations on user recipes
- Apply various tags to recipes
- Add ingredients to recipes
- Add recipe images
- Filter their recipes by TAGS or INGREDIENTS

# Technologies in use / Tech Stack / Built with

- Django
- Django Rest Framework
- Docker
- Python

# Installation

## To install RECIPE APP API locally, please follow the steps below:

- First, ensure you have the following installed on your machine
    - Python
    - Docker Desktop
    - Git
- Clone repo to your machine `git clone <repository URL>`
- cd into the project directory
- Open the project in your desired IDE(e.g., Pycharm or VS code)
- Run the following commands
    - `pip install -r requirements.txt` to install the project dependencies
    - `docker-compose build` to build the projects docker image from the docker file
    - `docker-compose up` to run the projects docker containers
- Then go the project URL `http://127.0.0.1:8000/api/schema/swagger/` to view the API endpoints

# What I have learned

I learned the following from this project: -

- How to properly implement REST API best practices
- How both a Django rest framework and Docker are used together
- How to dockerize a django rest framework web application
- How to authenticate and authorize users in a web application
- How to properly write and structure my unit tests
- How to properly implement TDD(Test Driven Development) in an application
- How to serve static and media files using Docker
- How to deploy a dockerized application to the cloud (AWS) etc.

# What issues have I faced and how I resolved them?

On the start of the project, I already had a well-rounded knowledge of Django and Django rest framework but very limited
knowledge
on Docker and TDD(Test-driven development)
These where the following issues I faced:-

- I had a hard time writing the project docker and docker-compose.yaml files since it was my first time using docker I
  had to google alot of docker
  command and basic synthax how to manage and configure my project dependencies and directories for development and
  deployment. Luckily,
  thanks to my googling and use of chatGPT, I manage to at least get the containers running with the right settings
- The concept of TDD was very foreign to me, it really changed my approach to how I built this application.
  The fact I had to thoroughly think about how my code shows work before writing tests was very difficult for me because
  I have never approached any of my
  projects like this before. So I had to research on TDD using alot of Django YouTube videos where the instructor showed
  their viewers how it's being implemented their
  thought process and all


## Add Chef Endpoint

The 'add_chef' endpoint allows users to update the chef's name for a specific recipe. This endpoint is used to handle POST requests and requires authentication.

### Usage

- URL: `/api/recipes/{recipe_id}/add_chef/`
- Method: POST
- Headers:
  - Authorization: Token <user_token>
- Body:
  ```json
  {
    "chef_name": "<chef_name>"
  }
  ```

### Permissions

- Only the user who created the recipe can update the chef's name.

### Validation

- The chef's name field should only contain alphabetic characters.

```