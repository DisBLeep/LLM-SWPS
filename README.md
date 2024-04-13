# Instrukcja Obsługi Chatbota z Funkcjonalnością Embedding

## Opis Projektu
Projekt ten polega na budowie systemu umożliwiającego wyszukiwanie informacji w dokumentach PDF za pomocą zaawansowanych technik NLP (Natural Language Processing) i embeddingów tekstowych. System przetwarza teksty zawarte w dokumentach PDF, transformuje je do postaci embeddingów, a następnie pozwala na semantyczne wyszukiwanie informacji zgodnie z zapytaniami użytkownika. Jest to szczególnie przydatne w przypadku dużych zbiorów dokumentów, gdzie tradycyjne metody wyszukiwania mogą okazać się nieefektywne.

## Ważne Informacje
- **Klucz API**: Aby korzystać z systemu, konieczne jest posiadanie klucza API do ChatGPT. Klucz ten należy umieścić w pliku `key.txt` w głównym katalogu projektu. Plik `key.txt` powinien być dodany do `.gitignore`, aby uniknąć jego przypadkowego wgrania do repozytorium.

## Struktura Folderów
- `/Doc` - Folder zawierający dokumenty PDF, które mają być przetworzone.
- `/Saved` - Folder, w którym zapisywane są embeddingi tekstów.
- `/Logs` - Folder, w którym zapisywane są wyniki przetwarzania oraz wyniki zapytań użytkownika.

## Wymagania
- `requirements.txt` - Plik zawierający listę zależności wymaganych do uruchomienia projektu.
- `installreqs.bat` - Skrypt batch do instalacji wymaganych pakietów dla systemów Windows.

## Pliki Źródłowe
- `ourfuncs.py` - Zawiera definicje funkcji wykorzystywanych do przetwarzania dokumentów PDF i zarządzania zapytaniami.
- `main.py` - Główny skrypt do uruchamiania systemu, przetwarzania dokumentów i obsługi zapytań.

## Instrukcja Uruchomienia
1. Zainstaluj wymagane zależności używając skryptu `installreqs.bat`.
2. Umieść swoje dokumenty PDF w folderze `/Doc`.
3. Uruchom skrypt `main.py` z poziomu linii komend:

Skrypt przeprowadzi Cię przez proces przetwarzania dokumentów PDF, tworzenia embeddingów, oraz umożliwi przeprowadzenie zapytań do systemu.

## Przykładowe Użycie
Załóżmy, że chcesz znaleźć informacje na temat "Małego Księcia" w przetworzonych dokumentach:
- Uruchom `main.py` i podaj zapytanie: "Czy Mały Książę kochał różę?"
- System przetworzy zapytanie, znajdzie i wyświetli najbardziej relewantne fragmenty tekstów.
Przy rozpoczynaniu każdej nowej sesji zaleca się wyczyszczenie konsoli dla lepszej czytelności wyników.

## Obsługa Błędów
W przypadku wystąpienia błędów związanych z nieodnalezieniem plików, upewnij się, że wszystkie ścieżki są prawidłowo skonfigurowane i że odpowiednie pliki znajdują się w swoich folderach. Dodatkowo, regularnie sprawdzaj, czy klucz API jest aktualny i prawidłowo umieszczony w pliku `key.txt`.