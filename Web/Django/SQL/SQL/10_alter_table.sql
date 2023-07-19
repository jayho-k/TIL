CREATE TABLE articles(
  title TEXT NOT NULL,
  content TEXT NOT NULL
);

DROP TABLE articles

INSERT INTO articles
VALUES ('1st title','1st content');

-- 테이블 이름 변경
ALTER TABLE articles RENAME TO news;

ALTER TABLE news
ADD COLUMN create_at TEXT;

INSERT INTO news
VALUES ('2nd title', '2nd content', datetime('now'));

ALTER TABLE news
ADD COLUMN subtitle TEXT NOT NULL
DEFAULT 'subtitle';

ALTER TABLE news
RENAME COLUMN title TO main_title;

ALTER TABLE news
DROP COLUMN subtitle;