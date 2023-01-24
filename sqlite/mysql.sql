-- CREATE TABLE films(
--   name TEXT,
--   release_year INTEGER);

-- INSERT INTO films(name, release_year)
-- VALUES("AVATAR 3", 2023);

-- INSERT INTO films(name, release_year)
-- VALUES("MATRIX 4", 2022);

-- SELECT * FROM films
-- WHERE release_year = 2023;


-- ALTER TABLE films
-- ADD COLUMN Runtime INTEGER;


-- UPDATE films
-- SET Runtime = 210
-- WHERE name = "AVATAR 3";

ALTER TABLE films
ADD CONSTRAINT unique_release UNIQUE (release_year);


SELECT * FROM films;