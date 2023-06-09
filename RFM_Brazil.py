###########################
# Gerekli Kütüphanelerin Yüklenmesi
##########################

import datetime as dt
import pandas as pd

####################################
# Satır Sütun Ayarlarının Yapılması
###################################

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)
pd.set_option("display.float_format", lambda x: "%3f" %x)

######################################
# Verinin Bulunduğu kök dizinden okutulması ve kopyasının alınması
######################################
df_ = pd.read_csv("Miuul/ara haftası çalıma dökümanları/RFM/RFM/order_customer.csv")

df = df_.copy()

######################################
# Veri Hakkında Bilgi Edinme
######################################

def check_df(dataframe, head=10):
    print("############ Shape #########")
    print(dataframe.shape)
    print("############ First 10 Data #########")
    print(dataframe.head(head))

    print("############ Info #########")
    print(dataframe.info())

    print("############ Statical Data #########")
    print(dataframe.describe([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

    print("############ Null Data #########")
    print(dataframe.isnull().sum())

    print("############ Variable Types #########")
    print(dataframe.dtypes)


check_df(df)

# order_id                     object
# customer_unique_id           object
# order_purchase_timestamp     object
# price                       float64

# yukarıda görüleceği üzere order_purchase_timestamp değişkeni tarih tipinde olmasına rağmen burada object tipindedir.
# yapacağımız rfm analizi kapsamında bu değişkenin tarih tipine datetime a çevirmemiz gereklidir.
# diğer değişkenlerin tiplerinde herhangi bir değiştirme işlemi yapmamıza gerek yoktur.

#################################
# Veri tipi dönüşümlerinin yapılması
###################################

df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

df.info()

#  #   Column                    Non-Null Count   Dtype
# ---  ------                    --------------   -----
#  0   order_id                  112650 non-null  object
#  1   customer_unique_id        112650 non-null  object
#  2   order_purchase_timestamp  112650 non-null  datetime64[ns] => tipi tarih olarak değişti.
#  3   price                     112650 non-null  float64

df.head()

###################################
# Enson yapılan Satınalama Tarihi ve Analiz Yaptımız Tarihin Belirlenmesi
####################################

df["order_purchase_timestamp"].max()

today_date = dt.datetime(2018, 9, 5) # burada analiz tarihini belirlemde son satın alma tarihine 2 gün eklendi

type(today_date)

df.head()


#########################################
# Müşteri Özelinde Recency, Frequency ve Monetary Değerlerinin Hesaplanması İşlemi
#########################################


rfm = df.groupby("customer_unique_id").agg({"order_purchase_timestamp": lambda order_purchase_timestamp: (today_date - order_purchase_timestamp.max()).days,
                                            "order_id": lambda order_id: order_id.nunique(),
                                            "price": lambda price: price.sum()
                                            })


rfm.head()

#                                   order_purchase_timestamp  order_id      price
# customer_unique_id
# 0000366f3b9a7992bf8c76cfdf3221e2                       117         1 129.900000
# 0000b849f77a49e4a4ce2b2a4ca5be3f                       120         1  18.900000
# 0000f46a3911fa3c0805444483337064                       543         1  69.000000
# 0000f6ccb0745a6a4b88665a16c9f078                       327         1  25.990000
# 0004aac84e0df4da2b147fca70cf8255                       294         1 180.000000




##########################################
# Sütunlarda yer alan recency, frequency ve monetary isimlerinin değiştirilmesi
#########################################

rfm.columns = ["Receny", "Frequency", "Monetary"]

rfm.head()

#                                   Receny  Frequency   Monetary
# customer_unique_id
# 0000366f3b9a7992bf8c76cfdf3221e2     117          1 129.900000
# 0000b849f77a49e4a4ce2b2a4ca5be3f     120          1  18.900000
# 0000f46a3911fa3c0805444483337064     543          1  69.000000
# 0000f6ccb0745a6a4b88665a16c9f078     327          1  25.990000
# 0004aac84e0df4da2b147fca70cf8255     294          1 180.000000


##############################################
# Yukarıda Hesapladığımız Recency, Frequency ve Monetary değerlerine göre RFM SOKRLARININ HESAPLANMASI
##############################################

rfm["Recency_Score"] = pd.qcut(rfm["Receny"], 5, labels=[5, 4, 3, 2, 1])

rfm["Frequency_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["Monetary_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])

rfm.head()


#                                   Receny  Frequency   Monetary Recency_Score Frequency_Score Monetary_Score
# customer_unique_id
# 0000366f3b9a7992bf8c76cfdf3221e2     117          1 129.900000             4               1              4
# 0000b849f77a49e4a4ce2b2a4ca5be3f     120          1  18.900000             4               1              1
# 0000f46a3911fa3c0805444483337064     543          1  69.000000             1               1              2
# 0000f6ccb0745a6a4b88665a16c9f078     327          1  25.990000             2               1              1
# 0004aac84e0df4da2b147fca70cf8255     294          1 180.000000             2               1              5

##################################################
# Elde ettiğimiz Recency_Score ve Frequency_Score değerlerini kullanarak RF_SCORE değişkenin oluşturulması
##################################################

rfm["RF_SCORE"] = (rfm["Recency_Score"].astype(str) + rfm["Frequency_Score"].astype(str))

rfm.head()



#                                 Receny  Frequency   Monetary Recency_Score Frequency_Score Monetary_Score RF_SCORE
# customer_unique_id
# 0000366f3b9a7992bf8c76cfdf3221e2     117          1 129.900000             4               1              4       41
# 0000b849f77a49e4a4ce2b2a4ca5be3f     120          1  18.900000             4               1              1       41
# 0000f46a3911fa3c0805444483337064     543          1  69.000000             1               1              2       11
# 0000f6ccb0745a6a4b88665a16c9f078     327          1  25.990000             2               1              1       21
# 0004aac84e0df4da2b147fca70cf8255     294          1 180.000000             2               1              5       21


####################################################
# RF_SCORE değişkeni için segment tanımlarının oluşturulması. segment haritası oluşturulması.
####################################################

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

######################################################
#seg_map yardımı ile RF_SCORE ları segtmentlere çevrilmesi
######################################################

rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)

rfm.head()
rfm["segment"].value_counts()
#                                   Receny  Frequency   Monetary Recency_Score Frequency_Score Monetary_Score RF_SCORE      segment
# customer_unique_id
# 0000366f3b9a7992bf8c76cfdf3221e2     117          1 129.900000             4               1              4       41    promising
# 0000b849f77a49e4a4ce2b2a4ca5be3f     120          1  18.900000             4               1              1       41    promising
# 0000f46a3911fa3c0805444483337064     543          1  69.000000             1               1              2       11  hibernating
# 0000f6ccb0745a6a4b88665a16c9f078     327          1  25.990000             2               1              1       21  hibernating
# 0004aac84e0df4da2b147fca70cf8255     294          1 180.000000             2               1              5       21  hibernating

rfm.to_csv("rfm.csv")



# Yukarıda yaptıkalrımızı kısaca bir özetlersek:
# 1 -   Bu çalışmada bize lazım olacak olan kütüphaneleri programa dahil ettik.
# 2 -   Satır ve sütunlarda gözterilecek olan değişken ve gözlem sayısı ayarını yaptık
# 3 -   Virgünden sonra kaç basamak gösterileceğinin ayarını yaptık
# 4 -   Veriyi Bulunduğu Kök Dizininden Okuttuk
# 5 -   Verinin Kopyasını Aldık
# 6 -   Veri Hakkında Genel Bilgi Edindik
# 7 -   Veri Tipi Dönüşümü Olup Olmadığını Kontro Ettik varsa veri tipi dönüşümü yaptık.
# 8 -   Enson yapılan Satınalama Tarihi ve Analiz Yaptımız Tarihin Belirledik.
# 9 -   Müşteri Özelinde Recency, Frequency ve Monetary Değerlerinin Hesaplanması İşlemi Yaptık.
# 10 -  Sütun İsimlerinin  Recency, Frequency ve Monetary isimleri değiştirilmesi işlemini Yaptık.
# 11 -  Hesapladığımız Recency, Frequency ve Monetary değerlerine göre RFM SOKRLARININ HESAPLANMASI
# 12 -  Elde ettiğimiz Recency_Score ve Frequency_Score değerlerini kullanarak RF_SCORE değişkenini Oluşturduk.
# 13 -  segment haritasını tanımladık.
# 14 -  Bu segment haritası kullanılarak RF_SCORE ları segmentlere dönüştürüldü.
# 15 -  Son olarak rfm data frame csv dosyasına bsaılarak dışarı aktarıldı.

































