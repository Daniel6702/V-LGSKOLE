# VÆLGSKOLE — midlertidig hjemmeside

En **fuldt statisk**, dansk pre-launch hjemmeside til MobilePay-godkendelse. Ingen Django, database, frontend-framework, hostingabonnement eller betalingsintegration. Genbruger billeder og logo fra SchoolChoiceDK (eget projekt).

Indeholder:

- `index.html` — hvad tjenesten tilbyder, pris (29 kr. engangsbetaling), virksomheds- og kontaktoplysninger.
- `handelsbetingelser.html` — aftalepart, betaling, levering, fortrydelsesret, returnering/refusion, reklamation, klager og tvister.
- `privatlivspolitik.html` — behandling af oplysninger på **denne statiske side**.
- Responsive CSS og eksisterende VÆLGSKOLE-grafik. Ingen trackers, scripts eller checkout.

## 1. Opret hjemmeside med dine rigtige virksomhedsoplysninger

Hjemmesiden **kan ikke indsendes til MobilePay før følgende seks oplysninger er angivet**: præcis registreret virksomhedsnavn, CVR, offentlig adresse (vej/nr.), postnr./by, **fungerende modtager-e-mail** og telefonnummer.

> **Vigtigt:** `adgang@xn--vlgskole-j0a.dk` er oprettet som *afsenderadresse* hos Brevo. Det betyder ikke, at den kan **modtage** e-mails. Brug en reel, fungerende kontaktadresse. Undgå at offentliggøre en hemmelighed; men virksomhedens kontaktoplysninger er netop beregnet til at være offentlige.

På Linux:

```bash
unzip vaelgskole-github-pages.zip
cd vaelgskole-pages-repo
python3 build.py
```

Du bliver spurgt om de seks oplysninger én gang. Scriptet genererer den færdige hjemmeside i `docs/`. Dine indtastninger gemmes i `business.local.json`, som ignoreres af Git. Offentlige kontaktoplysninger **indgår i genererede HTML-filer**, som bliver offentlige ved publicering.

Hvis du vil ændre oplysningerne, kør:

```bash
python3 build.py --edit
```

Valider at siden er klar:

```bash
python3 build.py --check
```

## 2. Se siden lokalt

Kør fra projektmappen:

```bash
python3 -m http.server 8000 -d docs
```

Åbn `http://localhost:8000/`, gennemgå alle tre sider og kontrollér især stavemåden af firmaets CVR, adresse, telefon og fungerende kontakt-e-mail. Afslut med Ctrl+C.

## 3. Publicer på GitHub Pages

Opret et **nyt offentligt** GitHub-repository, fx `vaelgskole-info` (eller brug dit eget navn). Upload **hele indholdet af `vaelgskole-pages-repo/` efter at `python3 build.py` er kørt**. På GitHub:

1. Repository → **Settings** → **Pages**.
2. Vælg **Deploy from a branch**.
3. Vælg `main`, derefter **`/docs`**, klik **Save**.
4. Vent på deploy og klik **Visit site**. URL'en bliver omtrent `https://DIT-GITHUB-NAVN.github.io/vaelgskole-info/`.
5. Brug den offentlige GitHub Pages URL i MobilePays formular (ikke `vælgskole.dk`, medmindre du senere konfigurerer det domæne). Henvis til `.../handelsbetingelser.html` som link til handelsbetingelser.

**Der skal ikke ændres noget DNS hos Simply.com.** Vi bruger ikke det rigtige domæne endnu. `/docs` indeholder en `.nojekyll`-fil til GitHub Pages. Ønsker du Git-kommandoer i stedet for upload via webinterfacet:

```bash
git init
git add .
git commit -m "Add temporary VÆLGSKOLE information site"
git branch -M main
git remote add origin https://github.com/DIT-GITHUB-NAVN/vaelgskole-info.git
git push -u origin main
```

## 4. Når MobilePay spørger efter URL'er

- **Website:** URL fra GitHub Pages som ovenfor.
- **Terms of sale:** Den samme URL med `/handelsbetingelser.html` til sidst.

Der er **ingen betalingsknap** på denne midlertidige side; den oplyser tydeligt, at den rigtige tjeneste er under udvikling. Det er op til MobilePay at godkende en pre-launch side. Når det rigtige Django-site bliver lanceret, kan du skifte URL hos MobilePay.

## Vigtig afgrænsning

Betingelserne er skrevet som et **før-lancering-udkast**, der omtaler den planlagte løsning og ikke lover en allerede aktiv webshop. Før første betaling bør du verificere den konkrete digitale produkttype, fortrydelsesret, den endelige betalingsproces og den endelige privatlivspolitik. En betalingsløsning kan ikke aktiveres alene ved at publicere denne informationsside.

GitHub Pages' vilkår forbyder at bruge Pages som egentlig gratis driftsplatform for en webshop eller kommerciel SaaS. Denne repo er derfor kun en **midlertidig, ikke-transaktionsbaseret informationsside**. Flyt den, hvis GitHub eller MobilePay vurderer, at den er uden for deres krav.

### Kilder til opbygningen

- [Vipps MobilePay: Krav til din webside](https://vippsmobilepay.com/da-DK/krav-til-din-webside)
- [Forbrug.dk: Fortrydelsesret ved køb på nettet](https://forbrug.dk/regler/fortrydelsesret)
- [Forbrug.dk: Køb af digitale tjenester](https://forbrug.dk/emner/nethandel-og-digitale-tjenester/koeb-og-levering-af-digitalt-indhold)
- [GitHub: GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [GitHub Pages vilkår](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features)
