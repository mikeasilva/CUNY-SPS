/* Week 2 Assignment

   THE ASSIGNMENT:

   Choose six recent popular movies.  Ask at least five people that you know
   (friends, family, classmates, imaginary friends) to rate each of these movie
   that they have seen on a scale of 1 to 5.  Take the results (observations)
   and store them in a SQL database.  Load the information into an R dataframe.

   MY APPROACH:

   I will store the data in three distict normalized tables.  One will hold data
   on the reviewers.  Another will hold data on the films.  The final table will
   hold the the reviewer and film combinations with the associated rating.  I
   want this to be a self contained script.
*/

# Step 1: Create the new flix database
CREATE SCHEMA `flix` DEFAULT CHARACTER SET utf8 ;

CREATE TABLE `flix`.`reviewers` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE `flix`.`films` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE `flix`.`ratings` (
    `films_id` INT UNSIGNED NOT NULL,
    `reviewers_id` INT UNSIGNED NOT NULL,
    `rating` FLOAT UNSIGNED NOT NULL,
    PRIMARY KEY (`films_id` , `reviewers_id`)
);

# Step 3: Insert data into the tables

# First the reviewers.  The names have been changed to protect the innocent.
INSERT INTO `flix`.`reviewers`
  (`name`)
VALUES
  ('json'),
  ('Dr. Christensen, the Supreme'),
  ('Jesse'),
  ('Vid'),
  ('FamGuy');

# Next the films
INSERT INTO `flix`.`films`
  (`title`)
VALUES
  ('Avengers: Infinity War'),
  ('Black Panther'),
  ('Mission Impossible: Fallout'),
  ('Incredibles 2'),
  ('Deadpool 2'),
  ('Annihilation');

# Finally the ratings
INSERT INTO `flix`.`ratings`
  (`films_id`, `reviewers_id`, `rating`)
VALUES
  (1, 1, 4),
  (2, 1, 5),
  (3, 1, 3),
  (4, 1, 3),
  (5, 1, 1),
  (6, 1, 2),
  (1, 2, 3),
  (2, 2, 3),
  (3, 2, 3),
  (4, 2, 3),
  (5, 2, 3),
  (6, 2, 3),
  (1, 3, 1),
  (2, 3, 1),
  (3, 3, 1),
  (4, 3, 3),
  (5, 3, 1),
  (6, 3, 1),
  (1, 4, 1.5),
  (2, 4, 3),
  (3, 4, 1.5),
  (4, 4, 3.5),
  (5, 4, 1.5),
  (6, 4, 1.5),
  (1, 5, 4),
  (2, 5, 5),
  (3, 5, 4),
  (4, 5, 4),
  (5, 5, 3),
  (6, 5, 2);
