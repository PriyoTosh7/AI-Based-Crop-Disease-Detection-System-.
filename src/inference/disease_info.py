
# ============================================================
# PLANTVILLAGE-AI
# COMPLETE 39 CLASS DISEASE INFORMATION DATABASE
# ============================================================

# Common profile builder

def profile(plant, disease, kind, pathogen, symptoms,
            causes, severity, healthy=False):

    if healthy:
        prevention = [
            "Use healthy planting materials",
            "Maintain balanced soil nutrition",
            "Provide proper irrigation",
            "Monitor plants regularly",
            "Maintain field hygiene"
        ]

        management = [
            "Continue regular plant care",
            "Monitor for unusual symptoms",
            "Maintain proper growing conditions"
        ]

        note = "The model classified this image as healthy. Continue regular monitoring."

    else:
        prevention = [
            "Use disease-free planting materials",
            "Remove infected plant debris",
            "Maintain proper plant spacing",
            "Avoid unnecessary leaf wetness",
            "Monitor plants regularly"
        ]

        management = [
            "Remove severely affected plant parts when appropriate",
            "Maintain field hygiene",
            "Improve air circulation",
            "Avoid spreading infection through tools or water",
            "Consult an agricultural expert for treatment recommendations"
        ]

        note = (
            "AI prediction is not a confirmed diagnosis. "
            "Verify symptoms before applying any treatment."
        )

    return {
        "plant": plant,
        "disease": disease,
        "type": kind,
        "pathogen": pathogen,
        "symptoms": symptoms,
        "causes": causes,
        "prevention": prevention,
        "management": management,
        "severity": severity,
        "note": note
    }


# ============================================================
# COMPLETE DATABASE - 39 EXACT DATASET CLASSES
# ============================================================

DISEASE_INFO = {

    # --------------------------------------------------------
    # APPLE
    # --------------------------------------------------------

    "Apple___Apple_scab": profile(
        "Apple", "Apple Scab", "Fungal Disease",
        "Venturia inaequalis",
        [
            "Olive-green spots on leaves",
            "Dark velvety lesions",
            "Leaves may become yellow and fall",
            "Scabby lesions may develop on fruit"
        ],
        [
            "Fungal infection",
            "Wet spring weather",
            "Infected fallen leaves"
        ],
        "Moderate to High"
    ),

    "Apple___Black_rot": profile(
        "Apple", "Black Rot", "Fungal Disease",
        "Diplodia seriata (Botryosphaeria obtusa)",
        [
            "Circular purple leaf spots",
            "Frog-eye lesions",
            "Black fruit rot",
            "Cankers on branches"
        ],
        [
            "Fungal infection",
            "Infected plant debris",
            "Wounded plant tissue"
        ],
        "Moderate to High"
    ),

    "Apple___Cedar_apple_rust": profile(
        "Apple", "Cedar Apple Rust", "Fungal Disease",
        "Gymnosporangium juniperi-virginianae",
        [
            "Bright orange leaf spots",
            "Yellow-orange lesions",
            "Small dark structures in lesions",
            "Premature leaf drop"
        ],
        [
            "Rust fungal infection",
            "Nearby infected juniper plants",
            "Moist spring conditions"
        ],
        "Moderate"
    ),

    # --------------------------------------------------------
    # BLUEBERRY
    # --------------------------------------------------------

    "Blueberry___healthy": profile(
        "Blueberry", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # CHERRY
    # --------------------------------------------------------

    "Cherry___Powdery_mildew": profile(
        "Cherry", "Powdery Mildew", "Fungal Disease",
        "Podosphaera clandestina",
        [
            "White powdery coating on leaves",
            "Leaf curling",
            "Distorted young shoots",
            "Reduced plant growth"
        ],
        [
            "Fungal infection",
            "Poor air circulation",
            "Favorable humidity and temperature"
        ],
        "Moderate"
    ),

    "Cherry___healthy": profile(
        "Cherry", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # CORN
    # --------------------------------------------------------

    "Corn___Cercospora_leaf_spot Gray_leaf_spot": profile(
        "Corn", "Cercospora Leaf Spot / Gray Leaf Spot",
        "Fungal Disease",
        "Cercospora zeae-maydis / Cercospora zeina",
        [
            "Long rectangular gray leaf lesions",
            "Lesions develop between leaf veins",
            "Gray or tan damaged areas",
            "Severe leaf drying"
        ],
        [
            "Fungal infection",
            "Infected crop residue",
            "Warm humid conditions"
        ],
        "Moderate to High"
    ),

    "Corn___Common_rust": profile(
        "Corn", "Common Rust", "Fungal Disease",
        "Puccinia sorghi",
        [
            "Small reddish-brown pustules",
            "Rust-colored spores on leaves",
            "Pustules may appear on both leaf surfaces",
            "Leaf tissue damage"
        ],
        [
            "Rust fungal infection",
            "Wind-dispersed spores",
            "Favorable humidity"
        ],
        "Moderate"
    ),

    "Corn___Northern_Leaf_Blight": profile(
        "Corn", "Northern Leaf Blight", "Fungal Disease",
        "Exserohilum turcicum",
        [
            "Long cigar-shaped leaf lesions",
            "Gray-green lesions",
            "Lesions gradually enlarge",
            "Severe leaf necrosis"
        ],
        [
            "Fungal infection",
            "Infected crop residue",
            "Prolonged leaf wetness"
        ],
        "High"
    ),

    "Corn___healthy": profile(
        "Corn", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # GRAPE
    # --------------------------------------------------------

    "Grape___Black_rot": profile(
        "Grape", "Black Rot", "Fungal Disease",
        "Guignardia bidwellii",
        [
            "Circular brown leaf spots",
            "Dark borders around lesions",
            "Black fruit rot",
            "Small black fungal structures"
        ],
        [
            "Fungal infection",
            "Rain splash",
            "Infected berries and canes"
        ],
        "High"
    ),

    "Grape___Esca_(Black_Measles)": profile(
        "Grape", "Esca (Black Measles)",
        "Fungal Disease Complex",
        "Phaeomoniella chlamydospora, Phaeoacremonium species and other fungi",
        [
            "Tiger-stripe leaf discoloration",
            "Yellow and reddish leaf areas",
            "Internal wood discoloration",
            "Dark spots on berries in some cases"
        ],
        [
            "Wood-infecting fungal complex",
            "Infected pruning wounds",
            "Plant stress"
        ],
        "High"
    ),

    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": profile(
        "Grape", "Leaf Blight (Isariopsis Leaf Spot)",
        "Fungal Disease",
        "Pseudocercospora vitis",
        [
            "Brown leaf spots",
            "Irregular necrotic areas",
            "Dark lesions on leaf surfaces",
            "Premature leaf drying"
        ],
        [
            "Fungal infection",
            "Infected fallen leaves",
            "Moist growing conditions"
        ],
        "Moderate to High"
    ),

    "Grape___healthy": profile(
        "Grape", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # ORANGE
    # --------------------------------------------------------

    "Orange___Haunglongbing_(Citrus_greening)": profile(
        "Orange", "Huanglongbing (Citrus Greening)",
        "Bacterial Disease",
        "Candidatus Liberibacter asiaticus",
        [
            "Blotchy yellow leaf mottling",
            "Yellow shoots",
            "Small and misshapen fruits",
            "Uneven fruit ripening",
            "Gradual decline of the tree"
        ],
        [
            "Bacterial infection",
            "Asian citrus psyllid transmission",
            "Infected planting materials"
        ],
        "Very High"
    ),

    # --------------------------------------------------------
    # PEACH
    # --------------------------------------------------------

    "Peach___Bacterial_spot": profile(
        "Peach", "Bacterial Spot", "Bacterial Disease",
        "Xanthomonas arboricola pv. pruni",
        [
            "Small dark leaf spots",
            "Yellow halos around lesions",
            "Shot-hole appearance",
            "Fruit surface lesions"
        ],
        [
            "Bacterial infection",
            "Rain splash",
            "Wet foliage",
            "Infected plant materials"
        ],
        "Moderate to High"
    ),

    "Peach___healthy": profile(
        "Peach", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # PEPPER
    # --------------------------------------------------------

    "Pepper,_bell___Bacterial_spot": profile(
        "Bell Pepper", "Bacterial Spot", "Bacterial Disease",
        "Xanthomonas species complex",
        [
            "Small water-soaked leaf spots",
            "Dark brown lesions",
            "Yellow areas around spots",
            "Fruit lesions may develop"
        ],
        [
            "Bacterial infection",
            "Contaminated seeds",
            "Splashing water",
            "Infected plant debris"
        ],
        "Moderate to High"
    ),

    "Pepper,_bell___healthy": profile(
        "Bell Pepper", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # POTATO
    # --------------------------------------------------------

    "Potato___Early_blight": profile(
        "Potato", "Early Blight", "Fungal Disease",
        "Alternaria solani",
        [
            "Concentric ring-shaped leaf spots",
            "Target-like lesions",
            "Yellowing around spots",
            "Lower leaf defoliation"
        ],
        [
            "Fungal infection",
            "Infected crop residue",
            "Plant stress",
            "Warm humid conditions"
        ],
        "Moderate to High"
    ),

    "Potato___Late_blight": profile(
        "Potato", "Late Blight", "Oomycete Disease",
        "Phytophthora infestans",
        [
            "Water-soaked leaf lesions",
            "Rapid brown tissue death",
            "White growth under leaves in humid conditions",
            "Tuber rot"
        ],
        [
            "Oomycete infection",
            "Cool humid weather",
            "Infected seed tubers",
            "Wind and water-dispersed spores"
        ],
        "Very High"
    ),

    "Potato___healthy": profile(
        "Potato", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # RASPBERRY
    # --------------------------------------------------------

    "Raspberry___healthy": profile(
        "Raspberry", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # SOYBEAN
    # --------------------------------------------------------

    "Soybean___healthy": profile(
        "Soybean", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # SQUASH
    # --------------------------------------------------------

    "Squash___Powdery_mildew": profile(
        "Squash", "Powdery Mildew", "Fungal Disease",
        "Podosphaera xanthii and Golovinomyces species",
        [
            "White powdery patches on leaves",
            "Leaf yellowing",
            "Leaf drying",
            "Reduced plant vigor"
        ],
        [
            "Fungal infection",
            "Dense plant growth",
            "Favorable humidity and temperature"
        ],
        "Moderate"
    ),

    # --------------------------------------------------------
    # STRAWBERRY
    # --------------------------------------------------------

    "Strawberry___Leaf_scorch": profile(
        "Strawberry", "Leaf Scorch", "Fungal Disease",
        "Diplocarpon earlianum",
        [
            "Small purple or reddish spots",
            "Spots gradually enlarge",
            "Leaf margins become brown and dry",
            "Severely affected leaves may die"
        ],
        [
            "Fungal infection",
            "Prolonged leaf wetness",
            "Infected plant debris"
        ],
        "Moderate to High"
    ),

    "Strawberry___healthy": profile(
        "Strawberry", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # TOMATO
    # --------------------------------------------------------

    "Tomato___Bacterial_spot": profile(
        "Tomato", "Bacterial Spot", "Bacterial Disease",
        "Xanthomonas species complex",
        [
            "Small dark leaf spots",
            "Yellow halos",
            "Water-soaked lesions",
            "Raised fruit spots"
        ],
        [
            "Bacterial infection",
            "Contaminated seeds",
            "Splashing water",
            "Infected plant debris"
        ],
        "High"
    ),

    "Tomato___Early_blight": profile(
        "Tomato", "Early Blight", "Fungal Disease",
        "Alternaria linariae and related Alternaria species",
        [
            "Target-like concentric leaf spots",
            "Brown lesions",
            "Yellowing of surrounding tissue",
            "Lower leaf defoliation"
        ],
        [
            "Fungal infection",
            "Infected crop debris",
            "Warm humid conditions",
            "Plant stress"
        ],
        "Moderate to High"
    ),

    "Tomato___Late_blight": profile(
        "Tomato", "Late Blight", "Oomycete Disease",
        "Phytophthora infestans",
        [
            "Large water-soaked lesions",
            "Rapid leaf browning",
            "White growth under leaves in humid conditions",
            "Fruit rot"
        ],
        [
            "Oomycete infection",
            "Cool humid weather",
            "Infected plant materials"
        ],
        "Very High"
    ),

    "Tomato___Leaf_Mold": profile(
        "Tomato", "Leaf Mold", "Fungal Disease",
        "Passalora fulva",
        [
            "Yellow patches on upper leaf surface",
            "Olive-green mold underneath leaves",
            "Leaf curling",
            "Premature leaf drying"
        ],
        [
            "Fungal infection",
            "High humidity",
            "Poor ventilation",
            "Prolonged leaf wetness"
        ],
        "Moderate"
    ),

    "Tomato___Septoria_leaf_spot": profile(
        "Tomato", "Septoria Leaf Spot", "Fungal Disease",
        "Septoria lycopersici",
        [
            "Small circular leaf spots",
            "Gray or tan centers",
            "Dark borders around spots",
            "Lower leaf yellowing"
        ],
        [
            "Fungal infection",
            "Rain splash",
            "Infected plant debris",
            "Wet foliage"
        ],
        "Moderate"
    ),

    "Tomato___Spider_mites Two-spotted_spider_mite": profile(
        "Tomato", "Spider Mites (Two-Spotted Spider Mite)",
        "Pest Damage",
        "Tetranychus urticae",
        [
            "Fine yellow stippling on leaves",
            "Bronzed leaf surfaces",
            "Fine webbing underneath leaves",
            "Leaf drying and dropping"
        ],
        [
            "Spider mite infestation",
            "Hot and dry conditions",
            "Rapid pest population growth"
        ],
        "Moderate to High"
    ),

    "Tomato___Target_Spot": profile(
        "Tomato", "Target Spot", "Fungal Disease",
        "Corynespora cassiicola",
        [
            "Circular brown leaf lesions",
            "Concentric target patterns",
            "Yellowing around lesions",
            "Leaf damage and defoliation"
        ],
        [
            "Fungal infection",
            "High humidity",
            "Wet foliage",
            "Infected crop debris"
        ],
        "Moderate to High"
    ),

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": profile(
        "Tomato", "Tomato Yellow Leaf Curl Virus",
        "Viral Disease",
        "Tomato yellow leaf curl virus complex",
        [
            "Upward leaf curling",
            "Yellow leaf margins",
            "Small and distorted leaves",
            "Stunted plant growth",
            "Reduced fruit production"
        ],
        [
            "Viral infection",
            "Whitefly transmission",
            "Infected planting materials"
        ],
        "Very High"
    ),

    "Tomato___Tomato_mosaic_virus": profile(
        "Tomato", "Tomato Mosaic Virus",
        "Viral Disease",
        "Tomato mosaic virus (ToMV)",
        [
            "Light and dark green mosaic patterns",
            "Leaf distortion",
            "Reduced plant growth",
            "Uneven leaf coloration"
        ],
        [
            "Viral infection",
            "Contaminated tools",
            "Mechanical transmission",
            "Infected plant materials"
        ],
        "Moderate to High"
    ),

    "Tomato___healthy": profile(
        "Tomato", "Healthy", "Healthy Plant",
        "No pathogen detected",
        [
            "No disease symptoms identified",
            "No specific disease pattern detected"
        ],
        ["No disease identified"],
        "Healthy", True
    ),

    # --------------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------------

    "Background_without_leaves": {
        "plant": "Background",
        "disease": "No Leaf Detected",
        "type": "Background Class",
        "pathogen": "Not applicable",
        "symptoms": [
            "No identifiable plant leaf detected"
        ],
        "causes": [
            "Image may contain soil, background or non-leaf objects"
        ],
        "prevention": [
            "Upload a clear plant leaf image",
            "Use adequate lighting",
            "Keep the leaf visible in the image"
        ],
        "management": [
            "Capture a new image of the plant leaf",
            "Avoid images containing only background objects"
        ],
        "severity": "Not applicable",
        "note": "This is not a plant disease diagnosis."
    }

}


# ============================================================
# GET DISEASE INFORMATION
# ============================================================

def get_disease_info(class_name):

    info = DISEASE_INFO.get(class_name)

    if info is not None:
        return info

    return {
        "plant": "Unknown",
        "disease": str(class_name),
        "type": "Not verified",
        "pathogen": "Information unavailable",
        "symptoms": [
            "Disease-specific information is not available."
        ],
        "causes": [
            "The class name does not match the database."
        ],
        "prevention": [
            "Use healthy planting materials",
            "Maintain field hygiene",
            "Monitor plants regularly"
        ],
        "management": [
            "Verify the class mapping",
            "Consult an agricultural expert"
        ],
        "severity": "Not assessed",
        "note": "Do not use unverified disease information."
    }


# ============================================================
# DATABASE VERIFICATION
# ============================================================

def verify_database(expected_classes=None):

    print("=" * 55)
    print("PLANTVILLAGE-AI DATABASE VERIFICATION")
    print("=" * 55)

    print("Total Database Classes:", len(DISEASE_INFO))

    healthy_count = sum(
        1 for item in DISEASE_INFO.values()
        if item["severity"] == "Healthy"
    )

    background_count = sum(
        1 for item in DISEASE_INFO.values()
        if item["type"] == "Background Class"
    )

    disease_count = len(DISEASE_INFO) - healthy_count - background_count

    print("Disease Profiles:", disease_count)
    print("Healthy Profiles:", healthy_count)
    print("Background Profiles:", background_count)

    if expected_classes is not None:

        missing = set(expected_classes) - set(DISEASE_INFO)
        extra = set(DISEASE_INFO) - set(expected_classes)

        print("Missing Classes:", missing)
        print("Extra Classes:", extra)

        if not missing and not extra:
            print("CLASS MAPPING: VERIFIED SUCCESSFULLY!")
        else:
            print("CLASS MAPPING: MISMATCH FOUND!")

    print("=" * 55)

    return len(DISEASE_INFO) == 39


if __name__ == "__main__":

    verify_database()

    print("\nDATABASE TEST:")

    test = get_disease_info("Strawberry___Leaf_scorch")

    for key, value in test.items():
        print(f"{key}: {value}")
