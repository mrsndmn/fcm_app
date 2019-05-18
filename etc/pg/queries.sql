-- все пользователи, которые сделали больше 1000 запросов за последний месяц
select author_id, count(1) ac from stream_events where action_time > current_date - '30 days'::interval group by author_id having count(1) > 1000;

-- удаляем спамеров явных
mephi_uir=# delete from stream_events where author_id in (select author_id from stream_events group by author_id having count(1) > 1000);
DELETE 35343

-- сколько спамерских текстов
mephi_uir=# select event_text, count(1) as cnt from stream_events group by event_text having count(1) > 1000 order by cnt limit 100;

-- новые спам-фильтры
-- купить пакет документов

mephi_uir=# select count(1) from stream_events where event_text like '%купить пакет документов%';
-[ RECORD 1 ]
count | 5870


select tag, count(1) as ut from (select unnest(tags) as tag from stream_events) a group by tag order by ut desc;
tag      |   ut
---------------+--------
 tourism0      | 563228
 satisfaction4 | 273224
 tourism7      | 232284
 satisfaction1 | 202582
 politics3     | 184370
 politics5     | 161829
 tourism4      | 125666
 tourism16     | 114110
 politics4     |  95797
 tourism5      |  88872
 politics6     |  66821
 satisfaction0 |  52189
 tourism19     |  43112
 politics8     |  33539
 politics7     |  32288
 politics2     |  29949
 tourism9      |  29849
 tourism6      |  26867
 tourism21     |  26474
 tourism8      |  23891
 tourism3      |  23454
 tourism20     |   8848
 politics0     |   8071
 tourism13     |   5171
 tourism14     |   4979
 tourism1      |   3795
 tourism17     |   3300
 satisfaction3 |   2835
 satisfaction2 |   2636
 tourism10     |   2543
 tourism15     |   2167
 politics9     |   2154
 tourism18     |   1638
 tourism12     |   1048
 tourism2      |    963
 tourism11     |    317
 tourism22     |    225
 politics1     |     14


CREATE MATERIALIZED VIEW msk_stream_data
AS
select count(1) from stream_events where 'tourism0' = any(tags);


select tag, count(1) as ut from (select unnest(tags) as tag from msk_stream_events) a group by tag order by ut desc;