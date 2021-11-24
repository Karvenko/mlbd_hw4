from pyspark.sql.functions import monotonically_increasing_id, lower, regexp_replace, split, explode, array_max, col, desc, length, log

df = spark.read.option("header", True).csv("/srv/data/tripadvisor_hotel_reviews.csv")
n_docs = df.count()
tdf = df.select(monotonically_increasing_id().alias("rowId"), regexp_replace(lower(df.Review), '[^a-zA-Z ]+', '').alias("Review"))
tdf = tdf.select("rowId", explode(split(tdf.Review, " ")).alias("word"))
tf_df = tdf.groupBy("rowId", "word").count().filter(length(col("word")) > 0).select("rowId", "word", col("count").alias("tf_count"))
df_df = tf_df.groupBy("word").count().orderBy(desc("count")).limit(100).select("word", col("count").alias("df_count"))
tfidf_df = tf_df.join(df_df, tf_df.word == df_df.word, "left").select("rowId", tf_df.word, "tf_count", "df_count").dropna()
tfidf_df = tfidf_df.select("rowId", "word", (col("tf_count") * log(n_docs / col("df_count"))).alias("tf_idf"))
tfidf_df = tfidf_df.groupBy("rowId").pivot("word").sum("tf_idf").orderBy("rowId")

tfidf_df.show()
tfidf_df.filter(col("rowId") < 2).collect()

"""
Sample output:
[Row(rowId=0, area=None, arrived=2.1503674416789713, away=None, bar=None, bathroom=None, beach=None, beautiful=None, bed=1.6894684197038032, beds=None, best=None, better=None, big=None, bit=None, booked=None, breakfast=None, buffet=None, check=2.2233798764265202, city=None, clean=0.9851494071049807, close=None, comfortable=1.6755556083335037, day=None, days=None, definitely=None, desk=None, did=2.089865978824783, excellent=None, experience=2.0469366996619316, fantastic=None, floor=None, food=None, free=None, friendly=None, going=None, good=0.7921242185565862, got=1.5939900373832527, great=0.6201832216452906, helpful=None, hotel=0.4545761803844016, hotels=None, just=0.9741010072037023, large=None, like=1.3468221620400502, little=1.5374725464942618, lobby=None, location=0.9192720883993198, lot=None, loved=None, lovely=None, make=None, minutes=None, morning=2.069486862150803, need=None, new=None, nice=5.079033540877031, night=2.3028391757737507, nights=None, no=None, not=1.0495976123182775, nt=None, people=1.6026773507056353, perfect=None, place=None, pool=None, price=None, problem=None, quiet=None, quite=None, really=None, recommend=None, resort=None, restaurant=None, restaurants=None, reviews=1.8931100114137265, right=None, room=1.1308092434096984, rooms=None, say=None, service=None, shower=None, small=None, staff=None, stay=1.4156929191116763, stayed=None, street=None, th=None, think=None, time=None, times=None, took=2.190124761478928, trip=None, use=None, view=1.7897605898846938, walk=None, walking=2.077247863465692, want=None, water=None, way=None, went=None, wonderful=None), 

Row(rowId=1, area=None, arrived=2.1503674416789713, away=1.8506044057983786, bar=None, bathroom=3.1442520971533, beach=None, beautiful=None, bed=None, beds=2.2086112034301, best=1.569543584411053, better=3.686357258203058, big=None, bit=None, booked=1.864993143250478, breakfast=3.1741850088099524, buffet=None, check=None, city=None, clean=0.9851494071049807, close=None, comfortable=None, day=1.2654090872543564, days=None, definitely=None, desk=7.437352343068532, did=2.089865978824783, excellent=None, experience=None, fantastic=None, floor=None, food=None, free=1.8999381959665207, friendly=None, going=None, good=3.168496874226345, got=4.781970112149758, great=0.6201832216452906, helpful=1.3992123432568495, hotel=1.136440450961004, hotels=3.6826615380260987, just=None, large=None, like=2.6936443240801005, little=None, lobby=None, location=None, lot=None, loved=None, lovely=None, make=1.8979825238960102, minutes=None, morning=2.069486862150803, need=None, new=None, nice=1.0158067081754063, night=2.3028391757737507, nights=None, no=3.301258774916952, not=3.6735916431139715, nt=None, people=None, perfect=None, place=None, pool=None, price=None, problem=None, quiet=None, quite=None, really=1.4342259802751725, recommend=None, resort=None, restaurant=None, restaurants=None, reviews=None, right=None, room=2.2616184868193967, rooms=None, say=None, service=None, shower=None, small=None, staff=1.150413813314949, stay=0.7078464595558381, stayed=None, street=None, th=4.4074727753215335, think=None, time=None, times=None, took=2.190124761478928, trip=1.7398856006412087, use=None, view=1.7897605898846938, walk=None, walking=None, want=None, water=None, way=None, went=None, wonderful=None)]
"""
