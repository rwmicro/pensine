---
title: "Systèmes Embarqués"
domain: "Applied Sciences"
subdomain: "Computer Science > Hardware"
tags: [sciences-appliquées, informatique]
date: "2026-02-25"
---

# Systèmes Embarqués

Un système embarqué est un système informatique spécialisé, intégré dans un équipement plus large pour remplir une fonction précise. À la différence d'un ordinateur général, il est contraint en ressources (mémoire, puissance, énergie) et souvent soumis à des exigences temps réel.

## Caractéristiques fondamentales

| Caractéristique | Description |
|---|---|
| **Ressources limitées** | RAM en kilo-octets, Flash en mégaoctets |
| **Temps réel** | Respect de contraintes temporelles strictes |
| **Fiabilité** | Fonctionnement continu, souvent sans maintenance humaine |
| **Efficacité énergétique** | Batteries, harvesting, modes veille |
| **Interaction matérielle** | GPIO, ADC, DAC, bus (UART, SPI, I2C, CAN) |
| **Absence d'OS complet** | Bare-metal ou RTOS léger |

## Architecture d'un microcontrôleur

Un microcontrôleur (MCU) intègre sur une seule puce le processeur, la mémoire et les périphériques.

```
┌─────────────────────────────────────────────────┐
│              MICROCONTRÔLEUR                     │
│                                                  │
│  ┌──────────┐   ┌──────────┐   ┌─────────────┐  │
│  │   CPU    │   │  Flash   │   │    RAM      │  │
│  │  Core    │   │ (code)   │   │  (données)  │  │
│  └────┬─────┘   │ 256KB    │   │  64KB       │  │
│       │         └──────────┘   └─────────────┘  │
│  ┌────┴──────────────────────────────────────┐   │
│  │              Bus interne (AHB/APB)        │   │
│  └───┬──────┬──────┬──────┬──────┬──────┬───┘   │
│     GPIO  UART   SPI   I2C  Timer  ADC   DMA     │
└─────────────────────────────────────────────────┘
```

### ARM Cortex-M

Architecture ARM Cortex-M domine le marché des MCUs (STM32, nRF52, RP2040, ESP32).

| Famille | Caractéristiques | Usage |
|---|---|---|
| Cortex-M0/M0+ | Ultra-basse consommation, simple | Capteurs, IoT |
| Cortex-M3 | 32 bits, multiplicateur matériel | Applications générales |
| Cortex-M4 | FPU, DSP, SIMD | Audio, traitement signal |
| Cortex-M7 | Double issue, cache L1, TCM | Haute performance embarquée |
| Cortex-M33 | TrustZone (isolation sécurisée) | Sécurité IoT |

Registres ARM Cortex-M :
- `R0-R12` : registres généraux
- `R13 (SP)` : Stack Pointer
- `R14 (LR)` : Link Register (adresse de retour)
- `R15 (PC)` : Program Counter
- `xPSR` : Program Status Register (flags Z, N, C, V, T)

## Programmation bare-metal (C/C++)

Sans système d'exploitation, le programme tourne directement sur le matériel.

### Vecteur d'interruption et démarrage

```c
// startup.c — table des vecteurs d'interruption
__attribute__((section(".isr_vector")))
const uint32_t vector_table[] = {
    (uint32_t)&_estack,        // Adresse initiale du stack pointer
    (uint32_t)Reset_Handler,   // Handler de reset (point d'entrée)
    (uint32_t)NMI_Handler,
    (uint32_t)HardFault_Handler,
    // ... autres exceptions
    (uint32_t)SysTick_Handler, // Timer système
    // Interruptions périphériques
    (uint32_t)USART1_IRQHandler,
    (uint32_t)TIM2_IRQHandler,
};

void Reset_Handler(void) {
    // 1. Copier .data (variables initialisées) de Flash vers RAM
    // 2. Mettre .bss (variables non initialisées) à zéro
    // 3. Appeler main()
    SystemInit();
    main();
    while(1); // Ne doit jamais retourner
}
```

### Manipulation de registres matériels

```c
#include <stdint.h>

// Accès direct aux registres (MMIO — Memory-Mapped I/O)
#define RCC_BASE    0x40021000U
#define GPIOA_BASE  0x48000000U

#define RCC_AHBENR  (*(volatile uint32_t*)(RCC_BASE + 0x14))
#define GPIOA_MODER (*(volatile uint32_t*)(GPIOA_BASE + 0x00))
#define GPIOA_ODR   (*(volatile uint32_t*)(GPIOA_BASE + 0x14))

void led_init(void) {
    // Activer l'horloge de GPIOA
    RCC_AHBENR |= (1 << 17);

    // Configurer PA5 en sortie (bits 11:10 = 01)
    GPIOA_MODER &= ~(0x3 << 10);  // effacer les 2 bits
    GPIOA_MODER |=  (0x1 << 10);  // mettre à 01 (sortie)
}

void led_toggle(void) {
    GPIOA_ODR ^= (1 << 5);    // XOR sur le bit 5
}
```

### GPIO et interruptions

```c
// Configurer une interruption externe sur EXTI (STM32)
void button_init(void) {
    // Configurer PA0 en entrée avec pull-up
    GPIOA_MODER &= ~(0x3 << 0);   // mode entrée (00)
    GPIOA_PUPDR |=  (0x1 << 0);   // pull-up (01)

    // Configurer EXTI0 sur GPIOA
    SYSCFG->EXTICR[0] = 0x00;     // PA0 → EXTI0

    // Activer l'interruption sur front descendant
    EXTI->FTSR |= (1 << 0);
    EXTI->IMR  |= (1 << 0);       // démasquer l'interruption

    // Activer dans le NVIC
    NVIC_EnableIRQ(EXTI0_IRQn);
    NVIC_SetPriority(EXTI0_IRQn, 2);
}

// Handler d'interruption
void EXTI0_IRQHandler(void) {
    if (EXTI->PR & (1 << 0)) {
        EXTI->PR = (1 << 0);      // acquitter (écrire 1 pour effacer)
        led_toggle();
    }
}
```

## Bus de communication

### UART (Universal Asynchronous Receiver/Transmitter)

Communication série asynchrone, point à point.

```
TX ──→ RX   (données)
RX ←── TX
GND ── GND

Trame : [START(0)] [D0..D7] [PARITY] [STOP(1)]
Débits courants : 9600, 115200, 921600 bauds
```

```c
// Initialisation UART (registres directs)
void uart_init(uint32_t baudrate) {
    uint32_t clk = 72000000;  // 72 MHz
    USART1->BRR = clk / baudrate;
    USART1->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
}

void uart_putchar(char c) {
    while (!(USART1->SR & USART_SR_TXE));  // attendre que TXE soit libre
    USART1->DR = c;
}
```

### SPI (Serial Peripheral Interface)

Bus synchrone maître/esclave, haute vitesse, full-duplex, 4 fils.

```
MOSI (Master Out Slave In)
MISO (Master In Slave Out)
SCK  (Clock)
CS   (Chip Select, actif bas)
```

Modes (CPOL/CPHA) : 0/0, 0/1, 1/0, 1/1 — définissent la polarité et la phase de l'horloge.

### I2C (Inter-Integrated Circuit)

Bus synchrone multi-maître, 2 fils, adressage 7 bits (128 devices) ou 10 bits.

```
SDA (données, bidirectionnel, open-drain)
SCL (horloge)

Trame : [START] [ADDR 7b] [R/W] [ACK] [DATA] [ACK] ... [STOP]
Vitesses : Standard 100kHz, Fast 400kHz, Fast+ 1MHz
```

### CAN (Controller Area Network)

Bus différentiel robuste pour environnements industriels et automobiles (sans maître, CSMA/CD-AMP).

## RTOS (Real-Time Operating System)

Un RTOS fournit un ordonnanceur préemptif qui garantit les délais d'exécution des tâches.

### Concepts fondamentaux

```
Tâches (threads légers) : unité de base d'exécution
Scheduler : répartit le CPU entre tâches selon priorités
Tick : interruption périodique (1ms typiquement) pour le scheduling

Contraintes temps réel :
- Soft real-time : délai préférable mais dépassement tolérable (lecture vidéo)
- Hard real-time : délai absolu (airbag, contrôle industriel)
```

### FreeRTOS

RTOS open source le plus utilisé sur Cortex-M.

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"
#include "queue.h"

// Déclaration des tâches
void vTask_LED(void *pvParameters);
void vTask_Sensor(void *pvParameters);

// Handle de sémaphore pour synchronisation
SemaphoreHandle_t xSemaphore;

// Queue pour communication inter-tâches
QueueHandle_t xQueue;

int main(void) {
    // Créer la queue (10 éléments de type float)
    xQueue = xQueueCreate(10, sizeof(float));

    // Créer un sémaphore binaire
    xSemaphore = xSemaphoreCreateBinary();

    // Créer les tâches
    xTaskCreate(
        vTask_LED,        // fonction de la tâche
        "LED",            // nom (debug)
        128,              // taille de la stack (mots de 32 bits)
        NULL,             // paramètre passé à la tâche
        2,                // priorité (plus haute = plus prioritaire)
        NULL              // handle (optionnel)
    );

    xTaskCreate(vTask_Sensor, "Sensor", 256, NULL, 3, NULL);

    // Démarrer l'ordonnanceur (ne retourne jamais)
    vTaskStartScheduler();
}

void vTask_Sensor(void *pvParameters) {
    float valeur;
    for (;;) {
        valeur = lire_capteur();
        // Envoyer dans la queue (bloque 100ms si pleine)
        xQueueSend(xQueue, &valeur, pdMS_TO_TICKS(100));
        vTaskDelay(pdMS_TO_TICKS(50));  // 50ms — yield au scheduler
    }
}

void vTask_LED(void *pvParameters) {
    float valeur;
    for (;;) {
        // Attendre un élément de la queue (bloquant)
        if (xQueueReceive(xQueue, &valeur, portMAX_DELAY)) {
            if (valeur > SEUIL) led_on();
            else                led_off();
        }
    }
}
```

### Primitives de synchronisation

| Primitive | Usage | Notes |
|---|---|---|
| Semaphore binaire | Signalisation (ISR → tâche) | Pas de propriété |
| Semaphore à compteur | Ressources multiples | N tokens disponibles |
| Mutex | Section critique (tâche ↔ tâche) | Propriété + priority inheritance |
| Queue | Communication inter-tâches | Données typées, thread-safe |
| Event Group | Attendre plusieurs événements | Bits de flags |
| Stream Buffer | Flux de bytes (UART) | Lock-free single reader/writer |

### Problèmes temps réel courants

```c
// Priority Inversion : tâche haute priorité bloquée par tâche basse
// → Résolution : Priority Inheritance Protocol (FreeRTOS mutex)

// Deadlock : deux tâches s'attendent mutuellement
// Tâche A : prend mutex1, attend mutex2
// Tâche B : prend mutex2, attend mutex1
// → Résolution : ordre cohérent d'acquisition des mutexes

// Stack overflow (très courant sur MCU avec RAM limitée)
// → Activer configCHECK_FOR_STACK_OVERFLOW dans FreeRTOSConfig.h
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    // Traiter l'erreur fatale
    __BKPT(0);   // breakpoint
    while(1);
}
```

## Outils de développement

| Outil | Usage |
|---|---|
| **GCC ARM** (`arm-none-eabi-gcc`) | Compilateur croisé |
| **OpenOCD** | Interface JTAG/SWD, débogage |
| **GDB** | Débogueur (via OpenOCD) |
| **ST-Link / J-Link** | Sondes de débogage |
| **STM32CubeIDE** | IDE pour STM32 (Eclipse + HAL) |
| **PlatformIO** | Multi-plateforme (Arduino, STM32, ESP32) |
| **Segger RTT** | Console série via JTAG (ultra-rapide) |
| **Logic Analyzer** | Analyser les signaux UART/SPI/I2C |

## Considérations IoT et sécurité embarquée

```c
// Secure Boot : vérifier la signature du firmware avant exécution
// TrustZone (Cortex-M33) : isoler le code sécurisé du non-sécurisé
// Watchdog Timer : redémarrer en cas de blocage
HAL_IWDG_Init(&hiwdg);  // Initialiser le watchdog
HAL_IWDG_Refresh(&hiwdg);  // Rafraîchir régulièrement (sinon reset)

// Ne jamais stocker de clés en clair en Flash
// Utiliser l'OTP (One-Time Programmable) ou un coprocesseur sécurisé (ATECC608)
```

| Menace IoT | Contre-mesure |
|---|---|
| Extraction du firmware | Désactiver JTAG en production, chiffrer la Flash |
| Mise à jour malveillante | OTA signé + Secure Boot |
| Communication interceptée | TLS mutuellement authentifié (mTLS) |
| Side-channel (power analysis) | Masquage, implémentations constantes en temps |
| Hardcoded credentials | Provisionnement individuel à la fabrication |
