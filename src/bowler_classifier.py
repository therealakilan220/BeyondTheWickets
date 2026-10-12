"""
Bowler classification module for IPL dataset:
Categorizes all bowlers into 'Spin' or 'Pace'.
"""

SPINNERS = {
    'A Badoni', 'A Chandila', 'A Dananjaya', 'A Kumble', 'A Mishra', 'A Symonds', 'A Zampa',
    'AA Chavan', 'AA Jhunjhunwala', 'AA Kazi', 'Abdur Razzak', 'Ankit Sharma', 'AR Patel',
    'AS Roy', 'Ayush Badoni', 'B Aparajith', 'BJ Hodge', 'C Munro', 'CH Gayle', 'CL White',
    'CV Varun', 'D Kalyankrishna', 'DB Ravi Teja', 'DJ Hooda', 'DJ Hussey', 'DJ Thornely',
    'DNT Zondo', 'DP Nannes', 'DR Smith', 'FH Edwards', 'G Gambhir', 'GB Hogg', 'GD Phillips',
    'GH Vihari', 'GJ Maxwell', 'Gurkeerat Singh', 'Harbhajan Singh', 'Harpreet Brar',
    'I Malhotra', 'Iqbal Abdulla', 'J Suchith', 'J Syed Mohammad', 'JE Root', 'JP Duminy',
    'K Gowtham', 'KC Cariappa', 'KH Pandya', 'KP Pietersen', 'Kuldeep Yadav', 'Karanveer Singh',
    'Kumar Kartikeya', 'LPC Silva', 'LR Shukla', 'LS Livingstone', 'M Ashwin', 'M Markande',
    'M Muralitharan', 'M Theekshana', 'MB Parmar', 'MJ Clarke', 'MJ Guptill', 'MJ Santner',
    'MK Lomror', 'MK Tiwary', 'MN Samuels', 'Mujeeb Ur Rahman', 'N Rana', 'ND Doshi',
    'Noor Ahmad', 'P Chopra', 'P Dogra', 'P Dubey', 'P Negi', 'P Sahu', 'PC Valthaty',
    'PD Collingwood', 'PK Garg', 'PP Chawla', 'PP Ojha', 'PV Tambe', 'R Ashwin', 'R Parag',
    'R Powell', 'R Sai Kishore', 'R Sharma', 'R Shukla', 'R Tewatia', 'RA Jadeja', 'RA Tripathi',
    'RD Chahar', 'RG Sharma', 'RJ Peterson', 'RR Powar', 'RR Sarwan', 'Rashid Khan',
    'Ravi Bishnoi', 'S Badree', 'S Gopal', 'S Lamichhane', 'S Midhun', 'S Nadeem', 'S Sriram',
    'SB Jakati', 'SB Joshi', 'SC Ganguly', 'SD Chitnis', 'SE Rutherford', 'SK Raina',
    'SK Warne', 'SP Narine', 'SR Tendulkar', 'SS Iyer', 'Sunny Gupta', 'Suyash Sharma',
    'Swapnil Singh', 'T Shamsi', 'TL Suman', 'TM Dilshan', 'TM Head', 'TR Banton',
    'V Sehwag', 'VS Yeligati', 'Washington Sundar', 'Wanindu Hasaranga', 'W Hasaranga',
    'Y Gnaneswara Rao', 'Y Nagar', 'Y Venugopal Rao', 'YK Pathan', 'YS Chahal', 'Yuvraj Singh',
    'M Vettori', 'DL Vettori', 'B Botha', 'J Botha', 'Shakib Al Hasan', 'A Zampa', 'IS Sodhi',
    'BAW Mendis', 'M Muralidaran', 'C Green', 'CJ Green', 'Harpreet Singh', 'Kartik Tyagi',
    'Shahbaz Ahmed', 'M Shahrukh Khan', 'R Sanjay Yadav', 'Sanjay Yadav', 'Akshar Patel',
    'Washington Sundar', 'Mujeeb Ur Rahman', 'M Theekshana', 'Maheesh Theekshana',
    'Tanush Kotian', 'Manav Suthar', 'Allah Ghazanfar', 'AM Ghazanfar', 'V Chakravarthy',
    'Varun Chakravarthy', 'Shreyas Gopal', 'Mandeep Singh', 'Riyan Parag', 'Lalit Yadav',
    'Abhishek Sharma', 'Tilak Varma', 'NT Tilak Varma', 'D Hooda', 'Deepak Hooda',
    'Glenn Maxwell', 'Rachin Ravindra', 'Mitchell Santner', 'Ravi Bishnoi', 'Noor Ahmad'
}

def get_bowler_type(bowler_name: str) -> str:
    """
    Returns 'Spin' if the bowler is identified as a spin bowler, otherwise 'Pace'.
    """
    if bowler_name in SPINNERS:
        return 'Spin'
    # Check partial match if any
    for sp in SPINNERS:
        if sp.lower() in bowler_name.lower():
            return 'Spin'
    return 'Pace'
