# archedetector backend

## Requirements
- Postgres
- Maven
- Java 16.0.1

## Setup
Before running the backend for the first time, make sure you have a functional postgres database ready for it to use. Please see the readme in the `Search Engine/Data` directory to use a backup. Finally, you need to update the property fields `url`, `username` and `password` with the relevant values for your case. The properties file can be found at `src/main/resources/application.properties`.

Note that if the `spring.jpa.hibernate.ddl-auto` variable is set to `create-drop`, the `archedetector` database will be created on startup and dropped on exit. Setting it to `update` will read the existing database on startup and not wipe it on exit.

## Running the application
The application can be run from an IDE, or in the following way: https://stackoverflow.com/questions/47835901/how-to-start-up-spring-boot-application-via-command-line

Add maven to your path variables and navigate to the backend root folder. Now you should be able to run the project with the command `mvn spring-boot:run`.