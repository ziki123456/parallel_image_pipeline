# **Parallel Image Processing Pipeline – Dokumentace projektu**

Autor: *Tadeáš*

Škola: SPŠE Ječná

Předmět: Programové vybavení (PV)

Datum: 24.11.2025

---

# **1. Úvod**

Tento dokument popisuje návrh, architekturu, chování a technické detaily projektu **Parallel Image Processing Pipeline**, který slouží k paralelnímu zpracování obrázků pomocí více vláken. Cílem projektu je demonstrovat reálné použití souběžných procesů, synchronizace vláken a řízení sdílených zdrojů.

Aplikace automaticky načítá obrázky ze složky **input**, zpracovává je ve více vláknech (aplikuje filtrování, změnu velikosti nebo převod do grayscale) a ukládá výsledky do složky **output**. Celý proces probíhá paralelně, efektivně a bezpečně, za použití synchronizačních technik.

---

# **2. Zadání projektu**

Cílem projektu je vytvořit software, který:

* Umí **rozložit práci** do více paralelních vláken.
* Řeší **synchronizaci a komunikaci** mezi vlákny.
* Zpracovává reálný problém, ne simulaci.
* Dokáže čistě řídit **vznik, ukončení a koordinaci** vláken.
* Je plně použitelný v praxi.

Aplikace splňuje tyto požadavky prostřednictvím architektury loader–worker–saver, která odpovídá modelu producer–consumer.

---

# **3. Požadavky na uživatele a systém**

### **3.1 Uživatelské požadavky**

* Uživatel poskytne vstupní obrázky (PNG nebo JPG) ve složce **input/**.
* Program se spouští jednoduchým příkazem:

  ```
  python src/main.py
  ```
* Program nevyžaduje žádnou interakci uživatele během běhu.

### **3.2 Funkční požadavky**

* Načítání obrázků do fronty.
* Paralelní zpracování obrázků pomocí N worker vláken.
* Ukládání výsledků do výstupní složky.
* Možnost změny konfigurace (cesty, počet vláken, filtry).

### **3.3 Nefunkční požadavky**

* Bezpečnost: Správná synchronizace vláken, žádné race conditions.
* Spolehlivost: Čisté ukončení aplikace, žádné deadlocky.
* Výkon: Zpracování probíhá paralelně.
* Přenositelnost: Funguje na libovolném školním PC.

---

# **4. Architektura aplikace**

Aplikace je rozdělena do tří hlavních paralelních celků:

### 1. **Loader (producent)**

* Načítá cesty k obrázkům.
* Vkládá je do fronty `raw_queue`.
* Po dokončení vkládá **N sentinelů** pro ukončení workerů.

### 2. **Workeři (procesory)**

* Odebírají cesty z fronty.
* Zpracují obrázek (resize + grayscale).
* Vloží výsledek do `processed_queue`.
* Při sentinel hodnotě se ukončí a sníží počítadlo workerů.

### 3. **Saver (konzument)**

* Ukládá zpracované obrázky do složky `output`.
* Ukončí se, když:

  * `active_workers == 0` **a** `processed_queue` je prázdná.

---

# **5. Architektonické diagramy**

## **5.1 Big Picture Architecture**

```
 ┌────────────┐       ┌─────────────────┐       ┌─────────────┐
 │   Loader   │──────▶│     Workeři     │──────▶│    Saver    │
 │ (1 vlákno) │       │ (N vláken)      │       │ (1 vlákno)  │
 └────────────┘       └─────────────────┘       └─────────────┘
        │                     │                         │
        ▼                     ▼                         ▼
   raw_queue   ─────────▶ processed_queue ─────────▶  výstup
```

## **5.2 Class diagram (zjednodušený)**

```
+----------------+
|    Config      |
|----------------|
| input_dir      |
| output_dir     |
| num_workers    |
| resize_to      |
| grayscale      |
+----------------+

+----------------+        +----------------+        +----------------+
|    Loader      |        |   Processor    |        |     Saver      |
|----------------|        |----------------|        |----------------|
| loader_thread()|        | processor_thread() |    | saver_thread()|
+----------------+        +----------------+        +----------------+
```

---

# **6. Behaviorální diagram (Activity Flow)**

```
[START]
   │
   ▼
 Loader čte seznam souborů
   │
   ▼
 Vkládá cesty souborů do raw_queue
   │
   ▼
 Workeři odebírají položky z raw_queue
   │
   ▼
 Zpracování obrázků (resize, grayscale)
   │
   ▼
 Workeři vkládají hotové obrázky do processed_queue
   │
   ▼
 Saver ukládá obrázky do output/
   │
   ▼
 Kontrola: active_workers == 0?
   │
   ▼
[END]
```

---

# **7. Detailní popis běhu aplikace**

1. Loader vlákno projde obsah složky *input/*.
2. Platné obrázky vloží do `raw_queue`.
3. Pokud existuje 5 obrázků a 3 workeři, loader vloží 3 sentinely pro ukončení.
4. Workeři paralelně načítají obrázky a zpracovávají je.
5. Do `processed_queue` vkládají:

   ```
   (název_souboru, zpracovaný_obrázek)
   ```
6. Saver vlákno ukládá obrázky.
7. Jakmile:

   * všichni workeři skončí (
     `active_workers == 0`)
   * `processed_queue` je prázdná
     … aplikace končí.

---

# **8. Konfigurace programu**

Konfigurace je uložená v `config.py`:

```python
input_dir = "input"
output_dir = "output"
num_workers = 3
resize_to = (800, 800)
grayscale = True
```

Uživatel může upravit hodnoty bez zásahu do logiky aplikace.

---

# **9. Chybové stavy**

### **1. Špatná vstupní složka**

* Loader vypíše chybu: „Vstupní složka neexistuje“.

### **2. Poškozený obrázek**

* Worker zachytí výjimku a vypíše ji.
* Aplikace pokračuje dál.

### **3. Fronta je prázdná příliš dlouho**

* Saver čeká pomocí timeoutu a kontroluje active_workers.

### **4. Deadlock prevence**

* Ukončení workerů pomocí sentinelů.
* `active_workers` počítadlo chráněné lockem.

---

# **10. Testování a validace**

Byly provedeny tyto testy:

* Test s jedním obrázkem.
* Test s více obrázky různé velikosti.
* Test s různým počtem workerů.
* Test s prázdnou složkou input.
* Test poškozeného obrázku.

Ve všech případech aplikace běžela stabilně a správně ukončila všechna vlákna.

---

# **11. Známé bugy / omezení**

* Program nepodporuje GIF, BMP, WEBP.
* Při extrémně velkých obrázcích může být pomalejší.
* Nemá pokročilé logování do souboru.

---

# **12. Možnosti rozšíření**

* Přidání dalších filtrů (blur, contrast…).
* GUI rozhraní.
* Logování do souboru.
* Web rozhraní.

---

# **13. Závěr**

Projekt splňuje všechny požadavky zadání na paralelní a souběžné zpracování dat. Používá bezpečnou komunikaci mezi vlákny, pracuje rychle, stabilně a je snadno konfigurovatelný. Architektura je přehledná, udržitelná a připravená na další rozšíření.

---

# **14. Licenční a právní informace**

Aplikace je školní projekt a je poskytována bez záruky. Třetí strana využívá pouze knihovnu **Pillow**, která je zahrnuta v requirements.txt.
