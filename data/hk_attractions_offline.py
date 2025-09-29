"""
Offline Hong Kong attractions data for reliable prototype functionality
Curated list of popular Hong Kong attractions with accessibility information
"""

HK_ATTRACTIONS = [
    {
        'id': 'hk_001',
        'name': 'Victoria Peak',
        'name_zh': '太平山頂',
        'category': 'attraction',
        'description': 'Hong Kong\'s most popular tourist destination offering panoramic views of the city skyline, Victoria Harbour, and surrounding islands.',
        'district': 'Central and Western',
        'address': 'The Peak, Hong Kong Island',
        'latitude': 22.2711,
        'longitude': 114.1489,
        'phone': '+852 2849 0668',
        'website': 'https://www.thepeak.com.hk',
        'opening_hours': 'Daily 10:00-23:00',
        'admission_fee': 'Peak Tram: HKD 65 (Adult), HKD 30 (Child/Senior)',
        'cost_range': (30, 100),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'audio_guide': True,
            'notes': ['Peak Tram is wheelchair accessible', 'Sky Terrace has elevator access', 'Accessible toilets available']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'indoor_outdoor'
    },
    {
        'id': 'hk_002',
        'name': 'Star Ferry Pier (Tsim Sha Tsui)',
        'name_zh': '天星碼頭',
        'category': 'attraction',
        'description': 'Historic ferry service connecting Hong Kong Island and Kowloon since 1888. Scenic harbour crossing with stunning city views.',
        'district': 'Tsim Sha Tsui',
        'address': 'Tsim Sha Tsui Promenade, Kowloon',
        'latitude': 22.2940,
        'longitude': 114.1685,
        'phone': '+852 2367 7065',
        'website': 'https://www.starferry.com.hk',
        'opening_hours': 'Daily 06:30-23:30',
        'admission_fee': 'Ferry: HKD 2.7-3.4',
        'cost_range': (3, 10),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': False,
            'accessible_toilets': True,
            'step_free_access': False,
            'notes': ['Ramp access to ferry', 'Staff assistance available', 'Some stairs to upper deck']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'outdoor'
    },
    {
        'id': 'hk_003',
        'name': 'Hong Kong Space Museum',
        'name_zh': '香港太空館',
        'category': 'museum',
        'description': 'Interactive science museum with planetarium shows, space exhibitions, and hands-on displays about astronomy and space exploration.',
        'district': 'Tsim Sha Tsui',
        'address': '10 Salisbury Road, Tsim Sha Tsui, Kowloon',
        'latitude': 22.2947,
        'longitude': 114.1694,
        'phone': '+852 2721 0226',
        'website': 'https://hk.space.museum',
        'opening_hours': 'Mon, Wed-Fri 13:00-21:00, Sat-Sun 10:00-21:00 (Closed Tue)',
        'admission_fee': 'Exhibition: HKD 10, Planetarium: HKD 24-32',
        'cost_range': (10, 50),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'audio_guide': True,
            'braille_materials': True,
            'notes': ['Full wheelchair access', 'Audio descriptions available', 'Tactile exhibits for visually impaired']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'indoor'
    },
    {
        'id': 'hk_004',
        'name': 'Hong Kong Park',
        'name_zh': '香港公園',
        'category': 'park',
        'description': 'Urban oasis featuring gardens, aviary, conservatory, and tai chi garden. Perfect for relaxation and nature walks.',
        'district': 'Central',
        'address': '19 Cotton Tree Drive, Central, Hong Kong Island',
        'latitude': 22.2769,
        'longitude': 114.1628,
        'phone': '+852 2521 5041',
        'website': 'https://www.lcsd.gov.hk',
        'opening_hours': 'Daily 06:00-23:00',
        'admission_fee': 'Free',
        'cost_range': (0, 0),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'notes': ['Paved pathways throughout', 'Accessible aviary entrance', 'Rest areas with benches']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'outdoor'
    },
    {
        'id': 'hk_005',
        'name': 'Avenue of Stars',
        'name_zh': '星光大道',
        'category': 'attraction',
        'description': 'Waterfront promenade celebrating Hong Kong cinema with handprints of movie stars and spectacular harbour views.',
        'district': 'Tsim Sha Tsui',
        'address': 'Tsim Sha Tsui Promenade, Kowloon',
        'latitude': 22.2938,
        'longitude': 114.1719,
        'phone': '+852 2508 1234',
        'website': 'https://www.avenueofstars.com.hk',
        'opening_hours': '24 hours',
        'admission_fee': 'Free',
        'cost_range': (0, 0),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': False,
            'accessible_toilets': True,
            'step_free_access': True,
            'notes': ['Flat promenade walkway', 'Accessible viewing areas', 'Nearby accessible facilities']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'outdoor'
    },
    {
        'id': 'hk_006',
        'name': 'Wong Tai Sin Temple',
        'name_zh': '黃大仙祠',
        'category': 'attraction',
        'description': 'Famous Taoist temple known for fortune-telling and colorful architecture. Popular pilgrimage site for locals and tourists.',
        'district': 'Wong Tai Sin',
        'address': '2 Chuk Yuen Village, Wong Tai Sin, Kowloon',
        'latitude': 22.3420,
        'longitude': 114.1938,
        'phone': '+852 2327 8141',
        'website': 'https://www1.siksikyuen.org.hk',
        'opening_hours': 'Daily 07:00-17:30',
        'admission_fee': 'Free (Donations welcome)',
        'cost_range': (0, 20),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': False,
            'accessible_toilets': True,
            'step_free_access': False,
            'notes': ['Some stairs in temple areas', 'Ramp access to main hall', 'Staff assistance available']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'outdoor'
    },
    {
        'id': 'hk_007',
        'name': 'Hong Kong Museum of History',
        'name_zh': '香港歷史博物館',
        'category': 'museum',
        'description': 'Comprehensive museum showcasing Hong Kong\'s natural and cultural history from prehistoric times to modern day.',
        'district': 'Tsim Sha Tsui East',
        'address': '100 Chatham Road South, Tsim Sha Tsui East, Kowloon',
        'latitude': 22.3010,
        'longitude': 114.1722,
        'phone': '+852 2724 9042',
        'website': 'https://hk.history.museum',
        'opening_hours': 'Mon, Wed-Fri 10:00-18:00, Sat-Sun 10:00-19:00 (Closed Tue)',
        'admission_fee': 'HKD 10 (Free on Wed)',
        'cost_range': (0, 10),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'audio_guide': True,
            'notes': ['Full accessibility throughout', 'Audio guides available', 'Large print materials']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'indoor'
    },
    {
        'id': 'hk_008',
        'name': 'Central Market',
        'name_zh': '中環街市',
        'category': 'shopping',
        'description': 'Revitalized historic market building featuring local shops, cafes, and cultural spaces in the heart of Central.',
        'district': 'Central',
        'address': '93 Queen\'s Road Central, Central, Hong Kong Island',
        'latitude': 22.2823,
        'longitude': 114.1578,
        'phone': '+852 2234 7849',
        'website': 'https://www.centralmarket.hk',
        'opening_hours': 'Daily 08:00-22:00',
        'admission_fee': 'Free',
        'cost_range': (0, 200),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'notes': ['Modern accessibility features', 'Multiple elevators', 'Accessible parking available']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'indoor'
    }
]

HK_RESTAURANTS = [
    {
        'id': 'rest_001',
        'name': 'Maxim\'s Palace (City Hall)',
        'name_zh': '美心皇宮',
        'category': 'restaurant',
        'description': 'Traditional dim sum restaurant in a grand setting. Famous for authentic Cantonese cuisine and classic dim sum.',
        'district': 'Central',
        'address': '2/F, Low Block, City Hall, Central, Hong Kong Island',
        'latitude': 22.2816,
        'longitude': 114.1614,
        'phone': '+852 2521 1303',
        'website': 'https://www.maxims.com.hk',
        'opening_hours': 'Daily 11:00-15:00, 18:00-23:00',
        'cost_range': (150, 400),
        'cuisine_type': 'Cantonese',
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'notes': ['Elevator access to restaurant', 'Accessible seating available', 'Staff assistance provided']
        },
        'dietary_options': {
            'soft_meals': True,
            'vegetarian': True,
            'halal': False,
            'no_seafood': True,
            'notes': ['Steamed dishes available', 'Vegetarian dim sum options', 'Soft congee and noodles']
        },
        'elderly_friendly': True,
        'child_friendly': True
    },
    {
        'id': 'rest_002',
        'name': 'Café de Coral (Accessible Branch)',
        'name_zh': '大家樂',
        'category': 'restaurant',
        'description': 'Popular local fast food chain offering affordable Hong Kong-style meals with senior-friendly options.',
        'district': 'Tsim Sha Tsui',
        'address': 'Shop B2, Basement 2, Harbour City, Tsim Sha Tsui, Kowloon',
        'latitude': 22.2978,
        'longitude': 114.1684,
        'phone': '+852 2735 8888',
        'website': 'https://www.cafedecoral.com',
        'opening_hours': 'Daily 07:00-23:00',
        'cost_range': (30, 80),
        'cuisine_type': 'Hong Kong Style',
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'notes': ['Wide aisles', 'Accessible counter height', 'Easy-to-read menu boards']
        },
        'dietary_options': {
            'soft_meals': True,
            'vegetarian': True,
            'halal': False,
            'no_seafood': True,
            'notes': ['Congee and soft rice dishes', 'Steamed vegetables', 'Senior meal sets available']
        },
        'elderly_friendly': True,
        'child_friendly': True
    },
    {
        'id': 'rest_003',
        'name': 'Yum Cha (Central)',
        'name_zh': '飲茶',
        'category': 'restaurant',
        'description': 'Modern dim sum restaurant with innovative presentations and traditional flavors in a contemporary setting.',
        'district': 'Central',
        'address': '2/F, Podium Level 2, IFC Mall, Central, Hong Kong Island',
        'latitude': 22.2855,
        'longitude': 114.1577,
        'phone': '+852 2295 0238',
        'website': 'https://www.yumcharestaurant.com',
        'opening_hours': 'Daily 11:30-22:30',
        'cost_range': (200, 500),
        'cuisine_type': 'Modern Cantonese',
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'notes': ['Mall accessibility features', 'Spacious dining area', 'Accessible parking in mall']
        },
        'dietary_options': {
            'soft_meals': True,
            'vegetarian': True,
            'halal': False,
            'no_seafood': True,
            'notes': ['Steamed dim sum options', 'Vegetarian menu available', 'Soft texture dishes']
        },
        'elderly_friendly': True,
        'child_friendly': True
    }
]

HK_TRANSPORT_HUBS = [
    {
        'id': 'transport_001',
        'name': 'Central MTR Station',
        'name_zh': '中環站',
        'category': 'transport',
        'description': 'Major MTR interchange station connecting Island, Tsuen Wan, and Tung Chung lines. Fully accessible with lifts.',
        'district': 'Central',
        'address': 'Central, Hong Kong Island',
        'latitude': 22.2816,
        'longitude': 114.1578,
        'phone': '+852 2881 8888',
        'website': 'https://www.mtr.com.hk',
        'opening_hours': '24 hours (train service 06:00-01:00)',
        'cost_range': (0, 0),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'tactile_guide': True,
            'audio_announcements': True,
            'notes': ['Multiple lifts to all platforms', 'Tactile guide paths', 'Wide fare gates available']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'indoor'
    },
    {
        'id': 'transport_002',
        'name': 'Tsim Sha Tsui MTR Station',
        'name_zh': '尖沙咀站',
        'category': 'transport',
        'description': 'Key MTR station in Kowloon tourist area with connections to Tsuen Wan line and easy access to attractions.',
        'district': 'Tsim Sha Tsui',
        'address': 'Tsim Sha Tsui, Kowloon',
        'latitude': 22.2978,
        'longitude': 114.1722,
        'phone': '+852 2881 8888',
        'website': 'https://www.mtr.com.hk',
        'opening_hours': '24 hours (train service 06:00-01:00)',
        'cost_range': (0, 0),
        'accessibility': {
            'wheelchair_accessible': True,
            'has_elevator': True,
            'accessible_toilets': True,
            'step_free_access': True,
            'tactile_guide': True,
            'audio_announcements': True,
            'notes': ['Lift access to street level', 'Connected to shopping areas', 'Multiple accessible exits']
        },
        'elderly_friendly': True,
        'child_friendly': True,
        'weather_suitability': 'indoor'
    }
]

def get_all_offline_venues():
    """Get all offline venue data combined"""
    return HK_ATTRACTIONS + HK_RESTAURANTS + HK_TRANSPORT_HUBS

def get_venues_by_category(category):
    """Get venues filtered by category"""
    all_venues = get_all_offline_venues()
    return [venue for venue in all_venues if venue['category'] == category]

def get_accessible_venues():
    """Get venues that are wheelchair accessible"""
    all_venues = get_all_offline_venues()
    return [venue for venue in all_venues if venue['accessibility']['wheelchair_accessible']]

def get_elderly_friendly_venues():
    """Get venues suitable for elderly visitors"""
    all_venues = get_all_offline_venues()
    return [venue for venue in all_venues if venue.get('elderly_friendly', False)]

def get_free_venues():
    """Get venues with free admission"""
    all_venues = get_all_offline_venues()
    return [venue for venue in all_venues if venue['cost_range'][0] == 0]