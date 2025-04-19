# Lemmikki-sovellus

Tämä on sovellus, joka antaa käyttäjille mahdollisuuden luoda profiileja lemmikeilleen, lisätä päivittäisiä tietoja lemmikkien toimista mm. ulkoilut, ruokailut jne. Käyttäjä pystyy myös jakamaan kuvia ja vuorovaikuttaa muiden käyttäjien kanssa.

## Toiminnallisuus

- Käyttäjäprofiilin luominen: Käyttäjä voi luoda oman käyttäjäprofiilin ja hallita omia tietojaan.
- Lemmikkien lisääminen: Käyttäjä voi lisätä lemmikkejä ja syöttää niille päivittäisiä tietoja, kuten ruokinta, aktiviteetit ja lääkitykset.
- Seuraaminen ja vuorovaikutus: Käyttäjä voi seurata ystäviensä lemmikkejä ja osallistua niiden aktiviteetteihin. Käyttäjä voi reagoida muiden lemmikkien toimintoihin, kuten kommenteilla ja tykkäyksillä.
- Lemmikkikuvien jakaminen ja reagoiminen: Käyttäjä voi jakaa lemmikkikuvia ja vuorovaikuttaa muiden käyttäjien jakamien kuvien kanssa (esim. tykkäykset ja kommentit).
- Lemmikkien jaottelu: Lemmikkejä voidaan jaotella eri kategorioihin, kuten koirat, kissat jne., sekä roduittain. Käyttäjät voivat suorittaa hakuja eri kategorioiden ja rotujen mukaan, mikä helpottaa lemmikkien löytämistä ja seurattavaksi valitsemista.
- Käyttäjä voi hakea lemmikkejä nimellä tai rodun perusteella.
- Hakutuloksista pääsee tarkkailemaan muiden lisäämiä lemmikkejä.
- Käyttäjät voivat tarkastella muiden käyttäjien profiileja lemmikkien tarkastelu sivulla olevan linkin kautta.
- Käyttäjä voi jättää kommentin toisen lemmikin profiiliin ja tarvittaessa poistaa tämän.

## Lemmikkien hallinta
- Käyttäjä voi lisätä lemmikkejä ja määrittää:
 - Lajin
 - Rodun
 - Lemmikin nimen ja kuvaus
- Käyttäjä voi poistaa lisätyn lemmikin
- Käyttäjä voi täydentää lemmikkiin päivittäisiä toimia:
 - Mahdollisuus lisätä kertoja mm.(Ulkoilu, ruokailu jne.)
 - Tietoihin tallentuu kellonaika ja päivän kerrat
 - Käyttäjä voi lisätä kuvan lemmikistä ja poistaa kuvan.


## Tekniset vaatimukset

- Sovellus on toteutettu Python-kielellä ja Flask-kirjastoa käyttäen.
- Sovellus käyttää SQLite-tietokantaa.
- Kehitystyössä on käytetty Git-versionhallintaa ja GitHub-palvelua.
- Sovelluksen käyttöliittymä muodostuu HTML-sivuista.

## Asennusohjeet

- Kloonaa projekti
- Luo virtuaaliympäristö ja aktivoi se
- Tarvittaessa asenna tarvittavat riippuvuudet
- Luo config.py tiedosto projektin juureen ja lisää sinne oma secret_key
- Alusta tietokanta komennolla sqlite3 database.db < schema.sql
- Käynnistä sovellus komennolla flask run

