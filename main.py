from ourfuncs import *

# Stałe konfiguracyjne używane w skrypcie
MODEL_EMBEDDING         = "text-embedding-3-small"  # Nazwa modelu do generowania osadzeń tekstowych
MODEL_NLP               = "gpt-3.5-turbo"           # Model przetwarzania języka naturalnego do interpretacji zapytań

# Prompt przekształcający pytanie użytkownika w stwierdzenie
PREPROMPT_CONVERT_PL    = "Przekształć następujące pytanie użytkownika w jasne, zwięzłe stwierdzenie, odpowiednie do semantycznego porównania z tekstami, takimi jak książki, podręczniki lub dokumenty prawne. Stwierdzenie powinno wyraźnie opisywać główne działanie lub problem związany z pytaniem, nie formułując go jako zapytanie."
PREPROMPT_CONVERT_EN    = "Convert the following user question into a clear, concise statement suitable for semantic comparison against texts such as books, manuals, or legal documents. The statement should explicitly describe the main action or concern of the question without posing it as a query."

# Ścieżki do plików z logami
PATH_LOG_QUERY          = "Logs/log_userqueries.pkl"     # Plik do zapisu zapytań użytkownika
PATH_LOG_RESULTS        = "Logs/log_searchresults.pkl"   # Plik do zapisu wyników wyszukiwania

# Ustawienia przetwarzania tekstów
SPLIT_REGEX             = r'\.\s+(?=[A-Z])'         # Regex do podziału tekstu na zdania
MIN_WORDS_IN_SENTENCE   = 3                         # Minimalna liczba słów w zdaniu
RESULTS_TOP_X           = 5                         # Liczba najbardziej podobnych zdań do wyświetlenia
RESULTS_CONTEXT_Y       = 3                         # Liczba zdań kontekstowych dookoła znalezionego zdania

def run(user_prompt):
    # Czyszczenie konsoli przed rozpoczęciem nowej operacji
    clear_console()
    print_line("Przetwarzanie dokumentów PDF...")

    # Przetwarzanie dokumentów PDF
    # Funkcja `process_pdfs` przeszukuje wskazany katalog w poszukiwaniu plików PDF,
    # ekstrahuje z nich tekst, dzieli na zdania i generuje osadzenia tekstowe dla każdego zdania.
    # Wyniki są zapisywane w plikach .pkl w podkatalogu `Saved`.
    process_pdfs(embedding_model= MODEL_EMBEDDING,
                 split_regex    = SPLIT_REGEX,
                 min_words      = MIN_WORDS_IN_SENTENCE)

    print_line("Przetwarzanie zapytania użytkownika...")
    # Przetwarzanie zapytania użytkownika
    # Funkcja `process_user_query` przetwarza zapytanie użytkownika w dwa kroki:
    # 1. Używa modelu GPT-3.5 do przekształcenia pytania w jasne, zwięzłe stwierdzenie.
    # 2. Generuje osadzenie semantyczne tego stwierdzenia.
    # Zwraca słownik z tekstem zapytania, jego osadzeniem oraz oryginalnym inputem użytkownika.
    user_query      = process_user_query( 
                        save_path       = PATH_LOG_QUERY,
                        pre_prompt      = PREPROMPT_CONVERT_PL,
                        model           = MODEL_NLP,
                        embedding_model = MODEL_EMBEDDING,
                        user_prompt     = user_prompt,
                        print_chat      = False)

    print_line("Wyszukiwanie tekstów związanych z zapytaniem...")
    clear_console()
    # Wyszukiwanie i wyświetlanie podobnych zdań
    # Funkcja `return_similar_sentences` wykonuje następujące kroki:
    # 1. Ładuje i łączy wszystkie przetworzone dane z plików .pkl.
    # 2. Oblicza podobieństwo kosinusowe między osadzeniem zapytania a osadzeniami zdań w danych.
    # 3. Sortuje zdania wg podobieństwa i wybiera top X.
    # 4. Dla każdego wybranego zdania znajduje i wyświetla Y zdań kontekstowych.
    # Zapisuje wyniki w pliku i opcjonalnie wyświetla je w konsoli.
    return_similar_sentences(
                        user_query, 
                        top_x           = RESULTS_TOP_X, 
                        context_y       = RESULTS_CONTEXT_Y,
                        results_path    = PATH_LOG_RESULTS,
                        print_results   = True)

# Uruchomienie funkcji z przykładowym zapytaniem
if __name__ == "__main__":
    run("Czy mały książe kochał różę?")

# Opcjonalne inspekcje danych (zakomentowane dla przejrzystości skryptu)
#inspect_pickle(PATH_LOG_QUERY)
#inspect_pickle(PATH_LOG_RESULTS, RESULTS_TOP_X)
