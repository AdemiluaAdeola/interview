import random
import statistics
import requests
import re
from collections import Counter
import psycopg2

"""
Python Basic Developer Test
Background:
You have been provided with a web page showing the colors of dresses put on by Bincom staffs for the week. We are planning to produce Tshirts for staffs and we have issues deciding the colors to be used. We want to make our decision based on the analysis of the data presented in the web page.

Kindly go through the web page and write a python program that answers the questions below:
 
Requirements:
·         You may use python2 or python3
·         You may use any IDE of your choice
·         You may use regular expression
 
Key Features:
1.      Which color of shirt is the mean color?
2.      Which color is mostly worn throughout the week?
3.      Which color is the median?
4.      BONUS Get the variance of the colors
5.      BONUS if a colour is chosen at random, what is the probability that the color is red?
6.      Save the colours and their frequencies in postgresql database
7.      BONUS write a recursive searching algorithm to search for a number entered by user in a list of numbers.
8.      Write a program that generates random 4 digits number of 0s and 1s and convert the generated number to base 10.
9.      Write a program to sum the first 50 fibonacci sequence.

"""



file_id = "1nf9WMDjZWIUnlnKyz7qomEYDdtWfW1Uf"
url = f"https://drive.google.com/uc?export=download&id={file_id}"

response = requests.get(url)
html_content = response.text

colors = re.findall(r'\b(Red|Blue|Green|Yellow|Orange|Pink|Brown|Black|White)\b', html_content, re.IGNORECASE)
colors = [c.capitalize() for c in colors]

"""
Problem 1: Finding the mean of the colors is best done using the python collections package since we are dealing with a list of strings.
"""
count = Counter(colors)

mean_color = count.most_common(1)[0][0]
print(mean_color)

"""
Problem 2: Finding the most common color is best done using the python collections package since we are dealing with a list
"""
most_common_color = count.most_common(1)[0][0]

print(most_common_color)

"""
Problem 3: Finding the mean using python inbuilt functions(sorted, len) to find the median
"""
color_counts = sorted(colors)

n = len(color_counts)
mid = n // 2

if n % 2 == 0:
    median_color = color_counts[mid - 1]
else:
    median_color = color_counts[mid]

print("Median shirt color is ", median_color)

"""
Problem 4: The color variace was particularly tricky but I had to research a lot more than I had to do for the other problems.
"""
color_map = {color: idx for idx, color in enumerate(set(colors))}
numeric_colors = [color_map[c] for c in colors]
variance_colors = statistics.pvariance(numeric_colors)

print(variance_colors)

"""Problem 5: Finding the probability that the shirt picked at random is res"""
prob_red = count["Red"] / len(colors)
print(prob_red)

"""
Problem 6: Building a function to save the colours and their frequencies in postgresql database and
to handle errors in the process if the database is not found to prevent the program from crashing.
"""
try:
    conn = psycopg2.connect(
        dbname="bincom_db",
        user="postgres",
        password="your_password",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS color_frequency (
            color VARCHAR(50),
            frequency INT
        )
    """)
    for c, f in count.items():
        cur.execute("INSERT INTO color_frequency (color, frequency) VALUES (%s, %s)", (c, f))
    conn.commit()
    cur.close()
    conn.close()
except Exception as e:
    print("DB Error:", e)

"""
Problem 7: Create recursive searching algorithm to search for a number entered by user in a list of numbers
"""
def recursive_search(lst, target, index=0):
    if index >= len(lst):
        return False
    if lst[index] == target:
        return True
    return recursive_search(lst, target, index+1)

print("Search 6 in list:", recursive_search([2,4,6,8,10], 6))

"""
Problem 8: Generating random 4-digit binary numbers and converting them to decimal
"""

binary_num = "".join(random.choice("01") for _ in range(4))
print("Binary:", binary_num, "Decimal:", int(binary_num, 2))

"""
Problem 9: Sum first 50 Fibonacci numbers using a function to handle the program better and easier
"""
 
def fibonacci_sum(n):
    a, b, total = 0, 1, 0
    for _ in range(n):
        total += a
        a, b = b, a + b
    return total

print("Sum first 50 Fibonacci:", fibonacci_sum(50))