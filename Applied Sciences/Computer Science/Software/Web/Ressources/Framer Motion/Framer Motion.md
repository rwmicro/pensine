---
title: "Framer Motion"
domain: "Applied Sciences"
subdomain: "Computer Science > Web > Ressources > Framer Motion"
tags: [sciences-appliquées, informatique, web]
date: "2026-02-04"
---

# Framer Motion

## Vue d'ensemble

Framer Motion est une bibliothèque d'animation production-ready pour React qui rend les animations complexes simples à implémenter avec une API déclarative.

## Installation

```bash
npm install framer-motion
# ou
yarn add framer-motion
```

## Concepts de base

### motion component

Transforme n'importe quel élément HTML/SVG en composant animable:

```jsx
import { motion } from 'framer-motion'

<motion.div />
<motion.button />
<motion.svg />
```

### Animations simples

```jsx
<motion.div
  animate={{ x: 100 }}
  transition={{ duration: 0.5 }}
/>
```

## Animation Properties

### Animate

**Position**
```jsx
<motion.div animate={{ x: 100, y: 50 }} />
```

**Scale & Rotate**
```jsx
<motion.div 
  animate={{ 
    scale: 1.5, 
    rotate: 180 
  }} 
/>
```

**Opacity**
```jsx
<motion.div animate={{ opacity: 0.5 }} />
```

**Color**
```jsx
<motion.div 
  animate={{ 
    backgroundColor: "#ff0000" 
  }} 
/>
```

### Initial

État initial avant animation:

```jsx
<motion.div
  initial={{ opacity: 0, y: -50 }}
  animate={{ opacity: 1, y: 0 }}
/>
```

### Transition

Contrôle du timing et de l'easing:

```jsx
<motion.div
  animate={{ x: 100 }}
  transition={{
    duration: 0.5,
    ease: "easeInOut",
    delay: 0.2
  }}
/>
```

**Types d'easing:**
- `"linear"`
- `"easeIn"`, `"easeOut"`, `"easeInOut"`
- `"circIn"`, `"circOut"`, `"circInOut"`
- `"backIn"`, `"backOut"`, `"backInOut"`
- Custom cubic bezier: `[0.17, 0.67, 0.83, 0.67]`

## Gestures

### Hover

```jsx
<motion.button
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.9 }}
>
  Click me
</motion.button>
```

### Tap/Click

```jsx
<motion.div
  whileTap={{ 
    scale: 0.95,
    rotate: 5 
  }}
/>
```

### Focus

```jsx
<motion.input
  whileFocus={{ scale: 1.05 }}
/>
```

### Drag

```jsx
<motion.div
  drag
  dragConstraints={{ 
    left: -100, 
    right: 100, 
    top: -100, 
    bottom: 100 
  }}
/>
```

**Drag direction:**
```jsx
<motion.div drag="x" /> // Horizontal only
<motion.div drag="y" /> // Vertical only
```

## Variants

Définir des animations réutilisables:

```jsx
const variants = {
  hidden: { opacity: 0, y: 50 },
  visible: { opacity: 1, y: 0 }
}

<motion.div
  variants={variants}
  initial="hidden"
  animate="visible"
/>
```

### Propagation de variants

```jsx
const list = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 50 },
  visible: { opacity: 1, y: 0 }
}

<motion.ul variants={list} initial="hidden" animate="visible">
  <motion.li variants={item} />
  <motion.li variants={item} />
  <motion.li variants={item} />
</motion.ul>
```

## AnimatePresence

Animer des éléments quand ils sont retirés du DOM:

```jsx
import { AnimatePresence } from 'framer-motion'

<AnimatePresence>
  {isVisible && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

### Mode

```jsx
<AnimatePresence mode="wait">
  {/* Un seul élément à la fois */}
</AnimatePresence>

<AnimatePresence mode="sync">
  {/* Animations simultanées */}
</AnimatePresence>
```

## Layout Animations

Animer automatiquement les changements de layout:

```jsx
<motion.div layout>
  Content
</motion.div>
```

### Shared Layout

```jsx
import { LayoutGroup } from 'framer-motion'

<LayoutGroup>
  <motion.div layoutId="card">
    Card content
  </motion.div>
</LayoutGroup>
```

## Scroll Animations

### useScroll

```jsx
import { useScroll } from 'framer-motion'

function Component() {
  const { scrollYProgress } = useScroll()
  
  return (
    <motion.div 
      style={{ scaleX: scrollYProgress }}
    />
  )
}
```

### whileInView

```jsx
<motion.div
  whileInView={{ opacity: 1 }}
  viewport={{ once: true }}
/>
```

## Hooks

### useAnimation

Contrôle programmatique:

```jsx
import { useAnimation } from 'framer-motion'

function Component() {
  const controls = useAnimation()
  
  useEffect(() => {
    controls.start({ x: 100 })
  }, [])
  
  return <motion.div animate={controls} />
}
```

### useMotionValue

Valeurs réactives:

```jsx
import { useMotionValue, useTransform } from 'framer-motion'

const x = useMotionValue(0)
const opacity = useTransform(x, [0, 100], [1, 0])

<motion.div 
  drag="x" 
  style={{ x, opacity }} 
/>
```

### useSpring

Animation avec physique:

```jsx
const x = useMotionValue(0)
const springX = useSpring(x, { stiffness: 100, damping: 10 })

<motion.div style={{ x: springX }} />
```

## SVG Animations

### Path drawing

```jsx
<motion.svg>
  <motion.path
    d="M 0 0 L 100 100"
    initial={{ pathLength: 0 }}
    animate={{ pathLength: 1 }}
    transition={{ duration: 2 }}
  />
</motion.svg>
```

### SVG variants

```jsx
const icon = {
  hidden: {
    opacity: 0,
    pathLength: 0,
    fill: "rgba(255, 255, 255, 0)"
  },
  visible: {
    opacity: 1,
    pathLength: 1,
    fill: "rgba(255, 255, 255, 1)"
  }
}
```

## Examples pratiques

### Fade In on Load

```jsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  Content
</motion.div>
```

### Stagger Animation

```jsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

<motion.div variants={container} initial="hidden" animate="show">
  {items.map(item => (
    <motion.div key={item} variants={item}>
      {item}
    </motion.div>
  ))}
</motion.div>
```

### Modal Animation

```jsx
<AnimatePresence>
  {isOpen && (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="overlay"
      />
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0, opacity: 0 }}
        className="modal"
      >
        Modal content
      </motion.div>
    </>
  )}
</AnimatePresence>
```

### Page Transitions

```jsx
import { AnimatePresence, motion } from 'framer-motion'
import { useRouter } from 'next/router'

function MyApp({ Component, pageProps }) {
  const router = useRouter()
  
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={router.route}
        initial={{ opacity: 0, x: -100 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 100 }}
        transition={{ duration: 0.3 }}
      >
        <Component {...pageProps} />
      </motion.div>
    </AnimatePresence>
  )
}
```

### Infinite Rotation

```jsx
<motion.div
  animate={{ rotate: 360 }}
  transition={{
    duration: 2,
    repeat: Infinity,
    ease: "linear"
  }}
/>
```

### Button with feedback

```jsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400, damping: 10 }}
>
  Click me
</motion.button>
```

## Performance Tips

1. **Use transform and opacity**
   - Plus performant que width/height
   - GPU accelerated

2. **Avoid animating expensive properties**
   - ❌ width, height, top, left
   - ✅ transform, opacity

3. **Use will-change sparingly**
   ```jsx
   <motion.div style={{ willChange: "transform" }} />
   ```

4. **Reduce motion for accessibility**
   ```jsx
   import { useReducedMotion } from 'framer-motion'
   
   const shouldReduceMotion = useReducedMotion()
   const duration = shouldReduceMotion ? 0 : 0.5
   ```

## Integration avec Next.js

```jsx
// _app.js
import { AnimatePresence } from 'framer-motion'

function MyApp({ Component, pageProps, router }) {
  return (
    <AnimatePresence mode="wait" initial={false}>
      <Component {...pageProps} key={router.route} />
    </AnimatePresence>
  )
}
```

## TypeScript Support

```tsx
import { motion, Variants } from 'framer-motion'

const variants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 }
}

<motion.div variants={variants} />
```

## Ressources

- [Documentation officielle](https://www.framer.com/motion/)
- [API Reference](https://www.framer.com/motion/api/)
- [Examples](https://www.framer.com/motion/examples/)
- [CodeSandbox Examples](https://codesandbox.io/s/framer-motion)

## Alternatives

- React Spring - Physics-based
- GSAP - Most powerful
- Anime.js - Lightweight
- React Transition Group - Basic

## Sujets à approfondir

- [ ] Complex gesture handling
- [ ] Custom spring configurations
- [ ] Performance optimization
- [ ] 3D transforms
- [ ] Motion values et MotionValue


*Dernière mise à jour: 2026-01-01*
