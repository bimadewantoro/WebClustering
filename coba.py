# Fungsi untuk membersihkan simbol dan angka dari teks
def remove_symbols_and_numbers(text):
    # Menggunakan ekspresi reguler untuk menghilangkan simbol dan angka
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
    return cleaned_text
    
# Terapkan remove_symbols_and_numbers pada kolom 'JudulSkripsi' dan membuat kolom baru judul_cleaned
df['judul_cleaned'] = df['JudulSkripsi'].apply(remove_symbols_and_numbers)
# Tokenisasi dan case folding pada kolom judul
df['judul_tokenized'] = df['judul_cleaned'].apply(lambda x: word_tokenize(str(x)))
df['judul_lower'] = df['judul_tokenized'].apply(lambda x: [word.lower() for word in x])
# stopword from file
list_stopwords = pd.read_csv("stopwords.txt", names= ["stopwords"], header = None)
# Function to remove stopwords
def stopwords_removal(words, stopwords):
    return [word for word in words if word.lower() not in stopwords]

# Read stopwords from the file stopwords.txt
with open('stopwords.txt', 'r') as file:
    stopwords = file.read().splitlines()

# Assuming 'data' contains the DataFrame and 'judul_lower' column is the list of words
# Apply stopwords_removal to each list in 'judul_lower' column
df['judul_no_stopwords'] = df['judul_lower'].apply(lambda x: stopwords_removal(x, stopwords))
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Function to perform stemming
def apply_stemming(words):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    stemmed_words = [stemmer.stem(word) for word in words]
    return ' '.join(stemmed_words)  # Join stemmed words back into a sentence

# Assuming 'data' contains the DataFrame and 'judul_lower' column is the list of words
# Apply stemming to each list in 'judul_lower' column
df['judul_stemmed'] = df['judul_no_stopwords'].apply(apply_stemming)
# Assuming 'data' contains the DataFrame and 'judul_stemmed' column has the stemmed text

# Initialize TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer()

# Fit and transform the stemmed text data using TF-IDF
tfidf_matrix = tfidf_vectorizer.fit_transform(df['judul_stemmed'])

# Convert TF-IDF matrix to DataFrame for further analysis
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names(), index=df.index)
from sklearn.cluster import KMeans

# Initialize KMeans clustering
num_clusters = 5  # Ubah jumlah kluster sesuai kebutuhan
kmeans = KMeans(n_clusters=num_clusters, random_state=42)

# Fit KMeans to the TF-IDF matrix
kmeans.fit(tfidf_matrix)

# Predict cluster labels for the data points
df['cluster_label'] = kmeans.labels_

# Optional: Print the cluster centers
print("Cluster Centers:")
print(kmeans.cluster_centers_)  # Centroids of clusters

# Optional: Analyze the cluster assignments
cluster_counts = df['cluster_label'].value_counts()
print("\nCluster Counts:")
print(cluster_counts)  # Number of data points in each cluster