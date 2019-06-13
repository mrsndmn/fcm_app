from fcm_app.config import arango_conn, pg_conn, config, logging, streaming_conf

classes = dict()
classes['spam'] = streaming_conf['rules']['global_alters']
classes['positive'] = ['хорошо', 'праздник', 'добро', 'счастье', 'благо', 'благополучие']
classes['negative'] = ['плохо', 'погибло', 'печаль', 'принуждение', 'ограничить'] # todo есть спорные
classes['crime'] = ['взятка', 'погибло', 'преступление']
classes['tourism'] = [] # from vkstream tags
classes['sport'] = [ 'соревнования', 'бег', 'спорт']
classes['culture'] = ['концерт', 'выставка', 'музей', "кино", "театр"] # todo geo tags todo laws

for k in classes:
    v = classes[k]
    print('ALTER TABLE stream_events add column {} boolean;'.format(k))
print("\n===========")

for k in classes:
    v = classes[k]
    query = ' | '.join(v)
    print('update stream_events set {} = true where text_tsvector @@ to_tsquery(\'{}\')\n'.format(k, query))


# update stream_events set spam = true where text_tsvector @@ to_tsquery('знакомства | ПАССАЖИРСКИЕ | перевозки | подселю | ОФОРМИ | ЗАЙМ | ОТКАЗА | ВНИМАНИЕ | СДАЮ | свингер | Prostata | займ | Познакомлюсь')

# update stream_events set positive = true where text_tsvector @@ to_tsquery('хорошо | праздник | добро | счастье | благо | благополучие')


# update stream_events set negative = true where text_tsvector @@ to_tsquery('плохо | погибло | печаль | преступление | принуждение | ограничить')
# update stream_events set crime    = true where text_tsvector @@ to_tsquery('взятка | погибло | преступление');
# update stream_events set tourism = true where 'tourism6|tourism3|tourism13|tourism14|tourism17|tourism10|tourism15|tourism18|tourism11|tourism22' ~!@# any(tags);

# update stream_events set sport = true where text_tsvector @@ to_tsquery('соревнования | бег | спорт');
# update stream_events set culture = true where text_tsvector @@ to_tsquery('концерт | выставка | музей | кино | театр');

# select
# count(spam)     as spam_cnt,
# count(positive)     as positive_cnt,
# count(negative)     as negative_cnt,
# count(crime)        as crime_cnt,
# count(tourism)      as tourism_cnt,
# count(sport)        as sport_cnt,
# count(culture)      as culture_cnt
# from stream_events;

# update stream_events set negative = true where crime;
# copy (select id, spam, positive, negative, crime, tourism, sport, culture from stream_events) to '/tmp/stream_events_classes.csv' with (format csv, header);

# spam_cnt | positive_cnt | negative_cnt | crime_cnt | tourism_cnt | sport_cnt | culture_cnt 
# ----------+--------------+--------------+-----------+-------------+-----------+-------------
#     19485 |        28549 |         1722 |       722 |       68024 |     15631 |       25540


(positive or negative or crime or tourism or sport or culture) and (spam is not null)
