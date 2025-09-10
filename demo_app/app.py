# app.py
import streamlit as st
import pandas as pd
import pickle
from geopy.geocoders import Nominatim

# --- モデル読み込み ---
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

st.title("民泊価格予測アプリ")

amenity_list = ['24-hour check-in', 'Accessible-height bed', 'Accessible-height toilet', 'Air conditioning', 'Air purifier', 'BBQ grill', 'Baby bath', 
 'Baby monitor', 'Babysitter recommendations', 'Bath towel', 'Bathtub', 'Bathtub with shower chair', 'Beach essentials', 'Beachfront', 'Bed linens', 
 'Body soap', 'Breakfast', 'Buzzer/wireless intercom', 'Cable TV', 'Carbon monoxide detector', 'Cat(s)', 'Changing table', 'Children’s books and toys', 
 'Children’s dinnerware', 'Cleaning before checkout', 'Coffee maker', 'Cooking basics', 'Crib', 'Disabled parking spot', 'Dishes and silverware', 'Dishwasher', 
 'Dog(s)', 'Doorman', 'Doorman Entry', 'Dryer', 'EV charger', 'Elevator', 'Elevator in building', 'Essentials', 'Ethernet connection', 'Extra pillows and blankets', 
 'Family/kid friendly', 'Fire extinguisher', 'Fireplace guards', 'Firm matress', 'Firm mattress', 'First aid kit', 'Fixed grab bars for shower & toilet', 'Flat', 
 'Flat smooth pathway to front door', 'Free parking on premises', 'Free parking on street', 'Game console', 'Garden or backyard', 'Grab-rails for shower and toilet', 
 'Ground floor access', 'Gym', 'Hair dryer', 'Hand or paper towel', 'Hand soap', 'Handheld shower head', 'Hangers', 'Heating', 'High chair', 'Host greets you', 'Hot tub', 
 'Hot water', 'Hot water kettle', 'Indoor fireplace', 'Internet', 'Iron', 'Keypad', 'Kitchen', 'Lake access', 'Laptop friendly workspace', 'Lock on bedroom door', 'Lockbox', 
 'Long term stays allowed', 'Luggage dropoff allowed', 'Microwave', 'Other', 'Other pet(s)', 'Outlet covers', 'Oven', 'Pack ’n Play/travel crib', 'Paid parking off premises', 
 'Path to entrance lit at night', 'Patio or balcony', 'Pets allowed', 'Pets live on this property', 'Pocket wifi', 'Pool', 'Private bathroom', 'Private entrance', 
 'Private living room', 'Refrigerator', 'Roll-in shower with chair', 'Room-darkening shades', 'Safety card', 'Self Check-In', 'Shampoo', 'Single level home', 
 'Ski in/Ski out', 'Smart lock', 'Smartlock', 'Smoke detector', 'Smoking allowed', 'Stair gates', 'Step-free access', 'Stove', 'Suitable for events', 'TV', 
 'Table corner guards', 'Toilet paper', 'Washer', 'Washer / Dryer', 'Waterfront', 'Well-lit path to entrance', 'Wheelchair accessible', 'Wide clearance to bed', 
 'Wide clearance to shower & toilet', 'Wide doorway', 'Wide entryway', 'Wide hallway clearance', 'Window guards', 'Wireless Internet', 'smooth pathway to front door']

property_type_list = ['Apartment', 'House', 'Townhouse', 'Loft', 'Cabin', 'Condominium','Guest suite', 'Guesthouse', 'Other', 'Bungalow', 'Villa', 'Bed & Breakfast',
'Dorm', 'Timeshare', 'Camper/RV', 'Cave', 'Hostel', 'Earth House', 'In-law', 'Serviced apartment', 'Boat' ,'Tent', 'Castle', 'Boutique hotel',
'Vacation home', 'Hut', 'Treehouse', 'Yurt', 'Chalet' ,'Island', 'Tipi', 'Train', 'Parking Space', 'Casa particular']

data = {}
data["accommodates"] = st.number_input("収容可能人数", min_value=1, max_value=20, value= 2, step=1)
data["amenities"] = st.multiselect("アメニティ (カンマ区切り)", amenity_list)
data["bathrooms"] = st.number_input("バスルーム数", min_value=1, max_value=20, value= 1, step=1)
data["bed_type"] = st.selectbox("ベッドタイプ", ['Real Bed', 'Pull-out Sofa', 'Futon', 'Couch', 'Airbed'])
data["bedrooms"] = st.number_input("ベッドルーム数", min_value=1, max_value=20, value= 1, step=1)
data["beds"] = st.number_input("ベッド数", min_value=1, max_value=20, value= 1, step=1)
data["cancellation_policy"] = st.selectbox("キャンセルポリシー", ['flexible', 'moderate', 'strict', 'super_strict_30', 'super_strict_60'])
data["city"] = st.selectbox("都市", ['LA','DC','NYC','SF','Chicago','Boston'])
data["cleaning_fee"] = st.selectbox("クリーニング料金含むか", ["t", "f"])
data["description"] = st.text_area("物件説明文（英語）")
data["instant_bookable"] = st.selectbox("即時予約可能か", ["t", "f"])
data["name"] = st.text_input("物件名（英語）")
data["property_type"] = st.selectbox("物件タイプ", property_type_list)
data["room_type"] = st.selectbox("部屋タイプ", ["Entire home/apt", "Private room", "Shared room"])
address = st.text_input("住所 (例: Manhattan, NY 10036, USA)")

if st.button("予測する"):
    # --- 住所から緯度経度を取得 ---
    geolocator = Nominatim(user_agent="airbnb_app")
    if address:
        try:
            location = geolocator.geocode(address)
            if location:
                data["latitude"] = location.latitude
                data["longitude"] = location.longitude
                data["zipcode"] = location.raw.get("postcode", None)
            else:
                st.warning("⚠️ 住所から緯度経度を取得できませんでした")
                data["latitude"] = None
                data["longitude"] = None
                data["zipcode"] = None
        except Exception as e:
            st.error(f"住所変換でエラーが発生しました: {e}")
            data["latitude"] = None
            data["longitude"] = None
            data["zipcode"] = None
    else:
        data["latitude"] = None
        data["longitude"] = None
        data["zipcode"] = None

    # --- DataFrame化 ---
    X = pd.DataFrame([data])

    # --- 必須カラム補完 ---
    required_cols = [
        "review_scores_rating",
        "host_identity_verified",
        "host_has_profile_pic",
        "host_since",
        "host_response_rate",
        "thumbnail_url",
        "first_review",
        "last_review",
        "number_of_reviews",
        "neighbourhood"
    ]

    for col in required_cols:
        if col not in X.columns:
            X[col] = None

    # --- ここで dtype を強制変換 ---
    force_float_cols = ["latitude", "longitude", "number_of_reviews"]
    for col in force_float_cols:
        if col in X.columns:
            X[col] = pd.to_numeric(X[col], errors="coerce").astype(float)

    # --- 予測 ---
    try:
        y_pred = model.predict(X)[0]
        st.success(f"予測価格: {y_pred:.0f} ドル/泊")
    except Exception as e:
        st.error(f"予測時にエラーが発生しました: {e}")


