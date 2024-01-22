from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from keras.models import load_model
from keras.preprocessing import sequence
import os
import imdb

from keras.datasets import imdb

class SentimentAnalyzer:

    def __init__(self, model_path='model.h5', review=None):
        #Ładuje model Keras, słownik mapujący słowa na indeksy
        # oraz odwrotny słownik mapujący indeksy na słowa.
        self.model = load_model(model_path)
        self.review = review
        self.word_index = imdb.get_word_index()
        self.reverse_word_index = dict([(value, key) for (key, value) in self.word_index.items()])

    def text_to_sequence(self, review_text):
        #zamienia recenzję na sekwencję tokenów za pomoca slownika.
        tokens = [self.word_index.get(word, 0) for word in review_text.split()]
        return sequence.pad_sequences([tokens], maxlen=10000)

    def predict_sentiment(self, review_text):
        # Predict_sentiment przewiduje sentyment na podstawie przetworzonej sekwencji tokenów.
        if review_text is None:
            raise ValueError("Review not provided.")

        tokens = self.text_to_sequence(review_text)
        prediction = self.model.predict(tokens)
        return prediction[0][0]


class ReviewWindow(QWidget):
    def __init__(self,model="model.h5"):
        super().__init__()
        self.reviews_list = []  # Lista przechowująca recenzje
        self.positive_reviews = 0  # Licznik pozytywnych recenzji
        self.negative_reviews = 0
        self.current_review_index = 0
        self.sentiment_analyzer = SentimentAnalyzer()
        self.setup()
        self.load_reviews()
        self.update_sentiment_counts()

    def setup(self):
        w = 600
        self.review=None
        self.load_reviews()


        self.setFixedSize(w, 600)
        self.setWindowTitle("Recenzje")

        pix_label = QLabel(self)
        pixmap = QPixmap("/Users/katarzyna/Documents/studia/zima 23:24/UM/projekt/shrek").scaled(200, 300)
        pix_label.setPixmap(pixmap)
        pix_label.move(20, 20)

        movie_title_label = QLabel("Movie Title: Shrek", self)
        movie_title_label.move(230,20)
        director_label = QLabel("Director: Andrew Adamson, Vicky Jenson", self)
        director_label.move(230,40)
        genre_label = QLabel("Genre: Animation, Comedy", self)
        genre_label.move(230,60)
        release_date_label = QLabel("Release Date: May 22, 2001", self)
        release_date_label.move(230,80)
        country_label = QLabel("Country of Origin: United States", self)
        country_label.move(230,100)
        movie_description_label = QLabel("Shrek, a content ogre living in a swamp, faces disruption\n"
                                         "when Lord Farquaad banishes fairy tale creatures to his home.\n"
                                         "In an effort to reclaim his swamp, Shrek, along with a talkative\n"
                                         "donkey, strikes a deal with Farquaad to rescue Princess Fiona\n"
                                         "from a tower guarded by a fire-breathing dragon.",self)
        movie_description_label.move(230,140)
        self.positive_txt=QLabel("Number of positive reviews: ", self)
        self.negative_txt=QLabel("Number of negative reviews: ", self)
        self.positive_txt.move(230,240)
        self.negative_txt.move(230,280)

        self.current_positive_reviews_txt = QLabel(str(self.positive_reviews), self)
        self.current_negative_reviews_txt = QLabel(str(self.positive_reviews), self)
        self.current_positive_reviews_txt.resize(100, 20)  # Zwiększono rozmiar etykiety
        self.current_negative_reviews_txt.resize(100, 20)
        self.current_positive_reviews_txt.move(410, 240)
        self.current_negative_reviews_txt.move(410, 280)

        self.review = QLineEdit("Enter a review", self)
        self.review.resize(450, 20)
        self.review.move(20, 350)

        add_button = QPushButton('Add', self)
        add_button.move(480, 345)
        add_button.clicked.connect(self.add_review)

        self.reviews_list_widget = QListWidget(self)
        self.reviews_list_widget.setGeometry(20, 380, 560, 200)
        self.show_reviews()

        self.show()

    def add_review(self):
        review_text = self.review.text()
        sentiment = self.sentiment_analyzer.predict_sentiment(review_text)

        if sentiment >= 0.5:
            self.positive_reviews += 1
        else:
            self.negative_reviews += 1

        self.reviews_list.append(self.review.text())
        print("Added review:", self.reviews_list)
        self.save_reviews()
        self.show_reviews()
        self.update_sentiment_counts()



    def show_reviews(self):
        # Wyczyszczenie listy przed ponownym dodaniem elementów
        self.reviews_list_widget.clear()

        if self.reviews_list:
            # Iteracja po wszystkich recenzjach w liście
            for review_text in self.reviews_list:
                # Dodanie recenzji do widżetu listy
                item = QListWidgetItem(review_text)
                self.reviews_list_widget.addItem(item)
        else:
            # Jeżeli brak recenzji, wyświetlenie odpowiedniego komunikatu
            item = QListWidgetItem("No reviews added yet.")
            self.reviews_list_widget.addItem(item)

    def update_sentiment_counts(self):
        # Zliczanie recenzji wprowadzonych przez użytkownika
        self.positive_reviews = sum(1 for sentiment in self.reviews_list_sentiments() if sentiment >= 0.5)
        self.negative_reviews = sum(1 for sentiment in self.reviews_list_sentiments() if sentiment < 0.5)

        # Aktualizacja etykiet z liczbami wszystkich recenzji
        self.positive_txt.setText(f"Number of positive reviews: ")
        self.negative_txt.setText(f"Number of negative reviews: ")

        # Aktualizacja etykiet z liczbami aktualnych recenzji
        self.current_positive_reviews_txt.setText(str(self.positive_reviews))
        self.current_negative_reviews_txt.setText(str(self.negative_reviews))


    def reviews_list_sentiments(self):
        # Zwraca sentymenty dla wszystkich recenzji w liście

        return [self.sentiment_analyzer.predict_sentiment(review_text) for review_text in self.reviews_list]

    def save_reviews(self):
        with open("reviews.txt", "w") as file:
            file.write("\n".join(self.reviews_list))

    def load_reviews(self):
        if os.path.exists("reviews.txt"):
            with open("reviews.txt", "r") as file:
                self.reviews_list = [line.strip() for line in file]
            print("Loaded reviews:", self.reviews_list)


if __name__ == "__main__":
    app = QApplication([])

    login_window = ReviewWindow()
    app.exec()
