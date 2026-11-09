# Popsy hero — concept fidelity correction, 9 November 2026

Source visual truth: output/research/home-hero-concepts-2026-11-09/popsy-hero-refined-v2.png (1585×992).
Mobile visual target: output/research/popsy-home-fidelity-2026-11-09/mobile-target-v2.png (977×1610 native image).
Implementation: output/concept/index.html, served and inspected in the Codex in-app browser at http://127.0.0.1:8765/.

## Comparison evidence

All files below are under output/research/popsy-home-fidelity-2026-11-09/.
- desktop-final.jpg: browser1585×992, same CSS size and density1 as source. No normalization.
- desktop-comparison-final.jpg: same-size source and implementation side by side, sourceleft.
- mobile-final.jpg: browser390×844, real76px site header.
- mobile-comparison-final.jpg: mobiletarget normalized to390width without stretching; native mock height643px, real implementation844px includes actual site header and a following-section preview. It is a composition reference, not a false1:1 viewport assertion.
- compact-final.jpg:320×568; landscape-final.jpg:640×360; tablet-final.jpg:768×1024; medium-desktop-final.jpg:1100×900.
- responsive-final.json: layout measurements320–1920px. Medium1100px was subsequently condensed and recaptured to remove excess vertical space.

## Findings and comparison history

The previous implementation was rejected by the user and is superseded, including its earlier visual acceptance. Its assets were materially different from the selected concept; functional correctness did not establish design fidelity.

1. [P1, resolved] Upright front package, different dull food group, missing crumbs/contact shadows and substituted font caption flattened the scene. Replaced all visual assets with source-grounded native ImageGen extractions: tilted package, exact-style golden-food grouping with crumbs and alpha contact shadows, real brush caption/underline and warm paper plate. Preserve original masters and previous runtime assets.
2. [P1, resolved] Phone products collided in an arbitrary overlap. Replaced negative offsets and giant overlapping canvases with visible-alpha-bound subject boxes, a controlled upper-left/lower-right diagonal and a separate compact treatment. Main390px silhouette gap reviewed visually; no pack-label obstruction. Phone title/caption/art/description/action now form one reading path.
3. [P2, resolved after independent design review] First revision still rendered food too muted. Measured warm-food sample means showed target216/127/33 versus render204/130/58. Corrected color with bounded CSS saturation; package has a subtle color/light correction. Final same-frame comparison reviewed and accepted.
4. [P2, resolved after independent design review] First phone revision placed package too low/large and food too small/low. Reduced package8%, raised it30px; enlarged food7% and raised it40px. Reduced excessive caption size, shortened scene height40px and raised CTA32px. Final390px hero ends726px; CTA ends703px; both fit844px viewport.
5. [P2, resolved] Short320px version brought crumbs too near description. Separated visible subject bounds and moved/reduced the prepared-food grouping; CTA remains fully visible, with no overflow.
6. [P2, resolved] Medium1100px viewport stretched the poster and left an accidental gap above the footer line. Height now follows the campaign aspect ratio and was recaptured; objects retain their layering and footer clearance.

Independent design review of final desktop1585×992 and phone390×844: no remaining P0/P1/P2 findings. Color, angle, shadows, crumbs, lettering, figure separation, hierarchy, planned negative space and CTA visibility were explicitly assessed. Generative extraction can differ in tiny printed details and is not claimed to be deterministic pixel segmentation.

## Required fidelity surfaces

- Typography: live poster H1 using existing Novoferma Protein; site Onest UI; handwritten source-style art retains the two lines and one tapered stroke, with accessible live text. Header and bottom-action scale aligned with selected concept.
- Spacing/layout: desktop positioning measured against source; phone diagonal composed independently; dedicated short phone, tablet and landscape rules; medium-width height follows image scale. No horizontal overflow measured at320,360,390,430,640,768,1024,1100,1280,1440,1585,1920.
- Colors: warm peachcream paper, chocolate title and source-style orange calligraphy; restored golden food and brighter package.
- Assets: genuine-alpha WebP, original tilt/perspective, separate food crumbs/shadows. No placeholder, entire-UI screenshot, fake SVG or CSS-drawn product. UI heading/description/links remain live. Raw PNG masters/prompts are research assets excluded from hosting.
- Copy: approved Попсы / Хрусти в своём ритме / mini-nugget description / О Попсах. No new product facts, prices or timing claims.

## Behavior and source checks

Native product CTA opens product-popsy.html in browser. No browser console errors observed. Existing bounded entrance/parallax and reduced-motion support retained; no perpetual animation. JS scenarios17/17 pass, including reduced motion and image-decode fallback. Static checks24 pages pass. New hero HTML matches scripts/popsy_home.py; lower homepage HTML is unchanged. Full generator was not run over direct edits.

## Published verification

https://novoferma-team-preview.vercel.app is READY at commit 6032c85ee6077922c1b192bbc74aa362ef7bb624. Finalizer confirmed the permanent version marker and noindex/robots. Published1585×992 desktop verified: restoredconceptassets loaded, no overflow, entrance complete. Final public screenshots saved in the same research directory as published-desktop.jpg and published-mobile.jpg.

Final result: passed
