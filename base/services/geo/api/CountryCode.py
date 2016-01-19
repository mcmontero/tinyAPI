# ----- Imports ---------------------------------------------------------------

import re

# ----- Public Classes --------------------------------------------------------

class CountryCode(object):
    '''
    Handles data and functionality for country codes.
    '''

    codes = {
        1: {
            "code": "1",
            "country_name": "United States"
        },

        2: {
            "code": "93",
            "country_name": "Afghanistan"
        },

        3: {
            "code": "355",
            "country_name": "Albania"
        },

        4: {
            "code": "213",
            "country_name": "Algeria"
        },

        5: {
            "code": "376",
            "country_name": "Andorra"
        },

        6: {
            "code": "244",
            "country_name": "Angola"
        },

        7: {
            "code": "672",
            "country_name": "Antarctica"
        },

        8: {
            "code": "54",
            "country_name": "Argentina"
        },

        9: {
            "code": "374",
            "country_name": "Armenia"
        },

        10: {
            "code": "297",
            "country_name": "Aruba"
        },

        11: {
            "code": "61",
            "country_name": "Australia"
        },

        12: {
            "code": "43",
            "country_name": "Austria"
        },

        13: {
            "code": "994",
            "country_name": "Azerbaijan"
        },

        14: {
            "code": "973",
            "country_name": "Bahrain"
        },

        15: {
            "code": "880",
            "country_name": "Bangladesh"
        },

        16: {
            "code": "375",
            "country_name": "Belarus"
        },

        17: {
            "code": "32",
            "country_name": "Belgium"
        },

        18: {
            "code": "501",
            "country_name": "Belize"
        },

        19: {
            "code": "229",
            "country_name": "Benin"
        },

        20: {
            "code": "975",
            "country_name": "Bhutan"
        },

        21: {
            "code": "591",
            "country_name": "Bolivia"
        },

        22: {
            "code": "387",
            "country_name": "Bosnia and Herzegovina"
        },

        23: {
            "code": "267",
            "country_name": "Botswana"
        },

        24: {
            "code": "55",
            "country_name": "Brazil"
        },

        25: {
            "code": "246",
            "country_name": "British Indian Ocean Territory"
        },

        26: {
            "code": "673",
            "country_name": "Brunei"
        },

        27: {
            "code": "359",
            "country_name": "Bulgaria"
        },

        28: {
            "code": "226",
            "country_name": "Burkina Faso"
        },

        29: {
            "code": "257",
            "country_name": "Burundi"
        },

        30: {
            "code": "855",
            "country_name": "Cambodia"
        },

        31: {
            "code": "237",
            "country_name": "Cameroon"
        },

        32: {
            "code": "1",
            "country_name": "Canada"
        },

        33: {
            "code": "238",
            "country_name": "Cape Verde"
        },

        34: {
            "code": "236",
            "country_name": "Central African Republic"
        },

        35: {
            "code": "235",
            "country_name": "Chad"
        },

        36: {
            "code": "56",
            "country_name": "Chile"
        },

        37: {
            "code": "86",
            "country_name": "China"
        },

        38: {
            "code": "61",
            "country_name": "Christmas Island"
        },

        39: {
            "code": "61",
            "country_name": "Cocos Islands"
        },

        40: {
            "code": "57",
            "country_name": "Colombia"
        },

        41: {
            "code": "269",
            "country_name": "Comoros"
        },

        42: {
            "code": "682",
            "country_name": "Cook Islands"
        },

        43: {
            "code": "506",
            "country_name": "Costa Rica"
        },

        44: {
            "code": "385",
            "country_name": "Croatia"
        },

        45: {
            "code": "53",
            "country_name": "Cuba"
        },

        46: {
            "code": "599",
            "country_name": "Curacao"
        },

        47: {
            "code": "357",
            "country_name": "Cyprus"
        },

        48: {
            "code": "420",
            "country_name": "Czech Republic"
        },

        49: {
            "code": "243",
            "country_name": "Democratic Republic of the Congo"
        },

        50: {
            "code": "45",
            "country_name": "Denmark"
        },

        51: {
            "code": "253",
            "country_name": "Djibouti"
        },

        52: {
            "code": "670",
            "country_name": "East Timor"
        },

        53: {
            "code": "593",
            "country_name": "Ecuador"
        },

        54: {
            "code": "20",
            "country_name": "Egypt"
        },

        55: {
            "code": "503",
            "country_name": "El Salvador"
        },

        56: {
            "code": "240",
            "country_name": "Equatorial Guinea"
        },

        57: {
            "code": "291",
            "country_name": "Eritrea"
        },

        58: {
            "code": "372",
            "country_name": "Estonia"
        },

        59: {
            "code": "251",
            "country_name": "Ethiopia"
        },

        60: {
            "code": "500",
            "country_name": "Falkland Islands"
        },

        61: {
            "code": "298",
            "country_name": "Faroe Islands"
        },

        62: {
            "code": "679",
            "country_name": "Fiji"
        },

        63: {
            "code": "358",
            "country_name": "Finland"
        },

        64: {
            "code": "33",
            "country_name": "France"
        },

        65: {
            "code": "689",
            "country_name": "French Polynesia"
        },

        66: {
            "code": "241",
            "country_name": "Gabon"
        },

        67: {
            "code": "220",
            "country_name": "Gambia"
        },

        68: {
            "code": "995",
            "country_name": "Georgia"
        },

        69: {
            "code": "49",
            "country_name": "Germany"
        },

        70: {
            "code": "233",
            "country_name": "Ghana"
        },

        71: {
            "code": "350",
            "country_name": "Gibraltar"
        },

        72: {
            "code": "30",
            "country_name": "Greece"
        },

        73: {
            "code": "299",
            "country_name": "Greenland"
        },

        74: {
            "code": "502",
            "country_name": "Guatemala"
        },

        75: {
            "code": "224",
            "country_name": "Guinea"
        },

        76: {
            "code": "245",
            "country_name": "Guinea-Bissau"
        },

        77: {
            "code": "592",
            "country_name": "Guyana"
        },

        78: {
            "code": "509",
            "country_name": "Haiti"
        },

        79: {
            "code": "504",
            "country_name": "Honduras"
        },

        80: {
            "code": "852",
            "country_name": "Hong Kong"
        },

        81: {
            "code": "36",
            "country_name": "Hungary"
        },

        82: {
            "code": "354",
            "country_name": "Iceland"
        },

        83: {
            "code": "91",
            "country_name": "India"
        },

        84: {
            "code": "62",
            "country_name": "Indonesia"
        },

        85: {
            "code": "98",
            "country_name": "Iran"
        },

        86: {
            "code": "964",
            "country_name": "Iraq"
        },

        87: {
            "code": "353",
            "country_name": "Ireland"
        },

        88: {
            "code": "972",
            "country_name": "Israel"
        },

        89: {
            "code": "39",
            "country_name": "Italy"
        },

        90: {
            "code": "225",
            "country_name": "Ivory Coast"
        },

        91: {
            "code": "81",
            "country_name": "Japan"
        },

        92: {
            "code": "962",
            "country_name": "Jordan"
        },

        93: {
            "code": "7",
            "country_name": "Kazakhstan"
        },

        94: {
            "code": "254",
            "country_name": "Kenya"
        },

        95: {
            "code": "686",
            "country_name": "Kiribati"
        },

        96: {
            "code": "383",
            "country_name": "Kosovo"
        },

        97: {
            "code": "965",
            "country_name": "Kuwait"
        },

        98: {
            "code": "996",
            "country_name": "Kyrgyzstan"
        },

        99: {
            "code": "856",
            "country_name": "Laos"
        },

        100: {
            "code": "371",
            "country_name": "Latvia"
        },

        101: {
            "code": "961",
            "country_name": "Lebanon"
        },

        102: {
            "code": "266",
            "country_name": "Lesotho"
        },

        103: {
            "code": "231",
            "country_name": "Liberia"
        },

        104: {
            "code": "218",
            "country_name": "Libya"
        },

        105: {
            "code": "423",
            "country_name": "Liechtenstein"
        },

        106: {
            "code": "370",
            "country_name": "Lithuania"
        },

        107: {
            "code": "352",
            "country_name": "Luxembourg"
        },

        108: {
            "code": "853",
            "country_name": "Macao"
        },

        109: {
            "code": "389",
            "country_name": "Macedonia"
        },

        110: {
            "code": "261",
            "country_name": "Madagascar"
        },

        111: {
            "code": "265",
            "country_name": "Malawi"
        },

        112: {
            "code": "60",
            "country_name": "Malaysia"
        },

        113: {
            "code": "960",
            "country_name": "Maldives"
        },

        114: {
            "code": "223",
            "country_name": "Mali"
        },

        115: {
            "code": "356",
            "country_name": "Malta"
        },

        116: {
            "code": "692",
            "country_name": "Marshall Islands"
        },

        117: {
            "code": "222",
            "country_name": "Mauritania"
        },

        118: {
            "code": "230",
            "country_name": "Mauritius"
        },

        119: {
            "code": "262",
            "country_name": "Mayotte"
        },

        120: {
            "code": "52",
            "country_name": "Mexico"
        },

        121: {
            "code": "691",
            "country_name": "Micronesia"
        },

        122: {
            "code": "373",
            "country_name": "Moldova"
        },

        123: {
            "code": "377",
            "country_name": "Monaco"
        },

        124: {
            "code": "976",
            "country_name": "Mongolia"
        },

        125: {
            "code": "382",
            "country_name": "Montenegro"
        },

        126: {
            "code": "212",
            "country_name": "Morocco"
        },

        127: {
            "code": "258",
            "country_name": "Mozambique"
        },

        128: {
            "code": "95",
            "country_name": "Myanmar"
        },

        129: {
            "code": "264",
            "country_name": "Namibia"
        },

        130: {
            "code": "674",
            "country_name": "Nauru"
        },

        131: {
            "code": "977",
            "country_name": "Nepal"
        },

        132: {
            "code": "31",
            "country_name": "Netherlands"
        },

        133: {
            "code": "599",
            "country_name": "Netherlands Antilles"
        },

        134: {
            "code": "687",
            "country_name": "New Caledonia"
        },

        135: {
            "code": "64",
            "country_name": "New Zealand"
        },

        136: {
            "code": "505",
            "country_name": "Nicaragua"
        },

        137: {
            "code": "227",
            "country_name": "Niger"
        },

        138: {
            "code": "234",
            "country_name": "Nigeria"
        },

        139: {
            "code": "683",
            "country_name": "Niue"
        },

        140: {
            "code": "850",
            "country_name": "North Korea"
        },

        141: {
            "code": "47",
            "country_name": "Norway"
        },

        142: {
            "code": "968",
            "country_name": "Oman"
        },

        143: {
            "code": "92",
            "country_name": "Pakistan"
        },

        144: {
            "code": "680",
            "country_name": "Palau"
        },

        145: {
            "code": "970",
            "country_name": "Palestine"
        },

        146: {
            "code": "507",
            "country_name": "Panama"
        },

        147: {
            "code": "675",
            "country_name": "Papua New Guinea"
        },

        148: {
            "code": "595",
            "country_name": "Paraguay"
        },

        149: {
            "code": "51",
            "country_name": "Peru"
        },

        150: {
            "code": "63",
            "country_name": "Philippines"
        },

        151: {
            "code": "64",
            "country_name": "Pitcairn"
        },

        152: {
            "code": "48",
            "country_name": "Poland"
        },

        153: {
            "code": "351",
            "country_name": "Portugal"
        },

        154: {
            "code": "974",
            "country_name": "Qatar"
        },

        155: {
            "code": "242",
            "country_name": "Republic of the Congo"
        },

        156: {
            "code": "262",
            "country_name": "Reunion"
        },

        157: {
            "code": "40",
            "country_name": "Romania"
        },

        158: {
            "code": "7",
            "country_name": "Russia"
        },

        159: {
            "code": "250",
            "country_name": "Rwanda"
        },

        160: {
            "code": "590",
            "country_name": "Saint Barthelemy"
        },

        161: {
            "code": "290",
            "country_name": "Saint Helena"
        },

        162: {
            "code": "590",
            "country_name": "Saint Martin"
        },

        163: {
            "code": "508",
            "country_name": "Saint Pierre and Miquelon"
        },

        164: {
            "code": "685",
            "country_name": "Samoa"
        },

        165: {
            "code": "378",
            "country_name": "San Marino"
        },

        166: {
            "code": "239",
            "country_name": "Sao Tome and Principe"
        },

        167: {
            "code": "966",
            "country_name": "Saudi Arabia"
        },

        168: {
            "code": "221",
            "country_name": "Senegal"
        },

        169: {
            "code": "381",
            "country_name": "Serbia"
        },

        170: {
            "code": "248",
            "country_name": "Seychelles"
        },

        171: {
            "code": "232",
            "country_name": "Sierra Leone"
        },

        172: {
            "code": "65",
            "country_name": "Singapore"
        },

        173: {
            "code": "421",
            "country_name": "Slovakia"
        },

        174: {
            "code": "386",
            "country_name": "Slovenia"
        },

        175: {
            "code": "677",
            "country_name": "Solomon Islands"
        },

        176: {
            "code": "252",
            "country_name": "Somalia"
        },

        177: {
            "code": "27",
            "country_name": "South Africa"
        },

        178: {
            "code": "82",
            "country_name": "South Korea"
        },

        179: {
            "code": "211",
            "country_name": "South Sudan"
        },

        180: {
            "code": "34",
            "country_name": "Spain"
        },

        181: {
            "code": "94",
            "country_name": "Sri Lanka"
        },

        182: {
            "code": "249",
            "country_name": "Sudan"
        },

        183: {
            "code": "597",
            "country_name": "Suriname"
        },

        184: {
            "code": "47",
            "country_name": "Svalbard and Jan Mayen"
        },

        185: {
            "code": "268",
            "country_name": "Swaziland"
        },

        186: {
            "code": "46",
            "country_name": "Sweden"
        },

        187: {
            "code": "41",
            "country_name": "Switzerland"
        },

        188: {
            "code": "963",
            "country_name": "Syria"
        },

        189: {
            "code": "886",
            "country_name": "Taiwan"
        },

        190: {
            "code": "992",
            "country_name": "Tajikistan"
        },

        191: {
            "code": "255",
            "country_name": "Tanzania"
        },

        192: {
            "code": "66",
            "country_name": "Thailand"
        },

        193: {
            "code": "228",
            "country_name": "Togo"
        },

        194: {
            "code": "690",
            "country_name": "Tokelau"
        },

        195: {
            "code": "676",
            "country_name": "Tonga"
        },

        196: {
            "code": "216",
            "country_name": "Tunisia"
        },

        197: {
            "code": "90",
            "country_name": "Turkey"
        },

        198: {
            "code": "993",
            "country_name": "Turkmenistan"
        },

        199: {
            "code": "688",
            "country_name": "Tuvalu"
        },

        200: {
            "code": "256",
            "country_name": "Uganda"
        },

        201: {
            "code": "380",
            "country_name": "Ukraine"
        },

        202: {
            "code": "971",
            "country_name": "United Arab Emirates"
        },

        203: {
            "code": "44",
            "country_name": "United Kingdom"
        },

        204: {
            "code": "598",
            "country_name": "Uruguay"
        },

        205: {
            "code": "998",
            "country_name": "Uzbekistan"
        },

        206: {
            "code": "678",
            "country_name": "Vanuatu"
        },

        207: {
            "code": "379",
            "country_name": "Vatican"
        },

        208: {
            "code": "58",
            "country_name": "Venezuela"
        },

        209: {
            "code": "84",
            "country_name": "Vietnam"
        },

        210: {
            "code": "681",
            "country_name": "Wallis and Futuna"
        },

        211: {
            "code": "212",
            "country_name": "Western Sahara"
        },

        212: {
            "code": "967",
            "country_name": "Yemen"
        },

        213: {
            "code": "260",
            "country_name": "Zambia"
        },

        214: {
            "code": "263",
            "country_name": "Zimbabwe"
        }
    }

    def get(self, id):
        self.__validate_id(id)

        return self.codes[id]['code']


    def get_country_name(self, id):
        self.__validate_id(id)

        return self.codes[id]['country_name']


    def __validate_id(self, id):
        if id not in self.codes.keys():
            raise RuntimeError('no such country code ID "{}"'.format(id))
