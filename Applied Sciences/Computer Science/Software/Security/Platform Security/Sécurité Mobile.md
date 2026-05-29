---
title: Sécurité Mobile — iOS et Android
domain: sciences-appliquées
subdomain: informatique / sécurité / platform-security
tags: [mobile, ios, android, sécurité, owasp, pentest, applications]
date: 2026-03-22
---

# Sécurité Mobile — iOS et Android

La sécurité mobile couvre la protection des appareils, systèmes d'exploitation et applications mobiles. Avec plus de 6 milliards de smartphones dans le monde, la surface d'attaque est considérable.

## Modèles de sécurité comparés

```mermaid
graph LR
    subgraph Android
        a_kernel[Linux Kernel]
        a_kernel --> a_hal[HAL]
        a_hal --> a_art[ART Runtime]
        a_art --> a_app[Application]
        a_sandbox[Sandbox par UID\nunique par app]
        a_perm[Système de permissions\nruntime / install-time]
    end

    subgraph iOS
        i_kernel[XNU Kernel / Darwin]
        i_kernel --> i_sec[Secure Enclave]
        i_kernel --> i_sand[Sandbox Seatbelt\n(profils par app)]
        i_sand --> i_app[Application]
        i_sign[Code Signing\nobligatoire]
        i_boot[Secure Boot Chain]
    end
```

| Aspect | Android | iOS |
|---|---|---|
| Noyau | Linux | XNU (BSD/Mach) |
| Sources | Open Source (AOSP) | Fermé |
| Distribution | Google Play + sideloading | App Store uniquement |
| Sandbox | UID Unix par app | Seatbelt profiles |
| Permissions | Dynamiques (runtime) | Dynamiques (runtime) |
| Chiffrement | Plein disque / par fichier | Data Protection (4 classes) |
| Jailbreak/Root | Plus fréquent | Plus difficile |

## OWASP Mobile Top 10

| # | Vulnérabilité | Description |
|---|---|---|
| M1 | Improper Credential Usage | Credentials codés en dur, mal stockés |
| M2 | Inadequate Supply Chain Security | SDK tiers malveillants, dépendances compromises |
| M3 | Insecure Authentication/Authorization | Authentification faible, bypass autorisation |
| M4 | Insufficient Input/Output Validation | XSS, injection via données externes |
| M5 | Insecure Communication | TLS absent, certificate pinning manquant |
| M6 | Inadequate Privacy Controls | Collecte de données excessive, logs sensibles |
| M7 | Insufficient Binary Protections | Pas d'obfuscation, débogage actif |
| M8 | Security Misconfiguration | Backup autorisé, debug mode en production |
| M9 | Insecure Data Storage | SharedPreferences non chiffrées, SQLite en clair |
| M10 | Insufficient Cryptography | Algorithmes faibles, mauvaise gestion des clés |

## Stockage insécurisé — Android

```java
// MAUVAIS — SharedPreferences non chiffrées
SharedPreferences prefs = getSharedPreferences("auth", MODE_PRIVATE);
prefs.edit().putString("token", accessToken).apply();
// Lisible dans /data/data/com.app/shared_prefs/ avec root

// MAUVAIS — Base SQLite non chiffrée
// Lisible dans /data/data/com.app/databases/

// BIEN — EncryptedSharedPreferences (Jetpack Security)
MasterKey masterKey = new MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build();
SharedPreferences encryptedPrefs = EncryptedSharedPreferences.create(
    context, "auth", masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
);

// BIEN — Android Keystore (clés non exportables, hardware-backed)
KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
```

## Stockage insécurisé — iOS

```swift
// MAUVAIS — UserDefaults en clair
UserDefaults.standard.set(token, forKey: "access_token")
// Stocké dans .plist lisible sans protection

// MAUVAIS — Documents/ directory (sauvegardé sur iCloud par défaut)

// BIEN — Keychain (chiffré, hardware-backed sur Secure Enclave)
let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "access_token",
    kSecValueData as String: tokenData,
    kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
]
SecItemAdd(query as CFDictionary, nil)

// BIEN — Data Protection class (chiffrement par état de l'appareil)
// NSFileProtectionCompleteUnlessOpen = chiffré sauf si fichier ouvert
```

## Communications non sécurisées

### Certificate Pinning

Vérifie que le certificat serveur correspond à un certificat connu (défense contre MITM même avec un CA compromis).

```java
// Android — OkHttp Certificate Pinning
OkHttpClient client = new OkHttpClient.Builder()
    .certificatePinner(new CertificatePinner.Builder()
        .add("api.example.com",
             "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        .build())
    .build();
```

```swift
// iOS — URLSession avec pinning manuel
func urlSession(_ session: URLSession,
                didReceive challenge: URLAuthenticationChallenge,
                completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
    guard let serverTrust = challenge.protectionSpace.serverTrust,
          let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
        completionHandler(.cancelAuthenticationChallenge, nil)
        return
    }
    // Comparer avec le certificat embarqué
}
```

**Contournement du pinning (test) :** Frida, objection, SSL Kill Switch 2, Proxyman.

## Jailbreak et Root

### Détection du jailbreak (iOS)

```swift
func isJailbroken() -> Bool {
    let paths = ["/Applications/Cydia.app", "/usr/sbin/sshd",
                 "/bin/bash", "/etc/apt", "/private/var/lib/apt/"]
    for path in paths {
        if FileManager.default.fileExists(atPath: path) { return true }
    }
    // Test d'écriture hors sandbox
    do {
        try "test".write(toFile: "/private/test.txt",
                         atomically: true, encoding: .utf8)
        return true
    } catch { return false }
}
```

**Contournement des détections :** Liberty Lite, A-Bypass, Shadow — les détections simples sont facilement contournables.

### Détection du root (Android)

```java
boolean isRooted() {
    String[] paths = {"/system/app/Superuser.apk", "/sbin/su",
                      "/system/bin/su", "/system/xbin/su"};
    for (String path : paths) {
        if (new File(path).exists()) return true;
    }
    try {
        Process p = Runtime.getRuntime().exec("su");
        return true;
    } catch (IOException e) { return false; }
}
```

**SafetyNet / Play Integrity API** : solution Google plus robuste pour attester l'intégrité de l'appareil.

## Analyse d'applications mobiles

### Android — APK

```bash
# Décompiler APK
apktool d application.apk -o decompiled/

# Décompiler DEX → Java (lisible)
jadx-gui application.apk

# Chercher des secrets codés en dur
grep -r "password\|secret\|api_key\|token" decompiled/ --include="*.xml" --include="*.smali"

# Analyser avec MobSF (framework automatique)
docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf

# Analyser les permissions dans AndroidManifest.xml
cat decompiled/AndroidManifest.xml | grep "uses-permission"
```

### iOS — IPA

```bash
# Extraire l'IPA
unzip app.ipa -d extracted/

# Analyser le binaire Mach-O
otool -L extracted/Payload/App.app/App    # Bibliothèques liées
nm -u extracted/Payload/App.app/App       # Symboles non résolus
strings extracted/Payload/App.app/App | grep -i "key\|token\|pass"

# Décompiler avec Ghidra ou Hopper Disassembler
# Analyser avec MobSF
```

### Analyse dynamique

```bash
# Frida — instrumentation dynamique (Android/iOS)
frida-ps -U                               # Lister les processus
frida -U -l script.js com.example.app    # Injecter un script

# Script Frida — hooker une méthode
Java.perform(function() {
    var MainActivity = Java.use('com.example.MainActivity');
    MainActivity.checkPassword.implementation = function(pass) {
        console.log('Password: ' + pass);
        return true;  // Bypass
    };
});

# objection — interface Frida simplifiée
objection -g com.example.app explore
# ios keychain dump
# android sslpinning disable
```

## Vecteurs d'attaque courants

### Intent Hijacking (Android)

Les Intents implicites peuvent être interceptés par une application malveillante.

```xml
<!-- Vulnérable : exported=true sans restriction -->
<activity android:name=".SecretActivity" android:exported="true"/>

<!-- Sécurisé : permission personnalisée -->
<activity android:name=".SecretActivity"
          android:exported="true"
          android:permission="com.example.CUSTOM_PERMISSION"/>
```

### Deep Links malveillants

```
myapp://reset-password?token=abc123
```

Si le token de reset est passé dans l'URL, un attaquant peut lancer ce deep link depuis une autre app.

### WebView XSS

```java
// MAUVAIS
webView.getSettings().setJavaScriptEnabled(true);
webView.addJavascriptInterface(new MyBridge(), "Android");
// Un XSS dans la WebView peut appeler les méthodes Java exposées

// BIEN — restreindre les origines
webView.getSettings().setAllowFileAccess(false);
webView.getSettings().setAllowContentAccess(false);
```

## Bonnes pratiques de développement sécurisé

| Domaine | Pratique |
|---|---|
| Stockage | Keychain (iOS) / Keystore + EncryptedSharedPreferences (Android) |
| Réseau | TLS 1.2+, certificate pinning, HSTS |
| Authentification | Biométrie + Keychain/Keystore, expiration des sessions |
| Code | Obfuscation (ProGuard/R8 Android, LLVM obfuscation iOS), pas de logs en prod |
| Permissions | Principe du moindre privilège, demander au moment de l'usage |
| Sauvegardes | Exclure les données sensibles des sauvegardes cloud |
| Intégrité | Détection root/jailbreak, Play Integrity API, SafetyNet |
| Secrets | Variables d'environnement CI, jamais dans le code source |
