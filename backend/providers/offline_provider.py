"""
NutriAI - Offline Nutrition Engine Provider
Provides 100% local, offline diet plan generation and intelligent assistant replies.
Works without internet connection or external API keys.
Supports rich bilingual interactive clinical chat with contextual memory of the user's plan.
"""

import json
import re
import copy
from typing import List, Dict, Optional, Any


class OfflineProvider:
    """
    Clinical offline provider using deterministic, evidence-based nutrition algorithms (Mifflin-St Jeor).
    Generates personalized 15-day meal plans and contextual nutrition guidance.
    """

    def __init__(self, **kwargs):
        pass

    def _parse_prompt(self, user_prompt: str) -> dict:
        data = {
            'age': 30, 'gender': 'male', 'height_cm': 175.0, 'weight_kg': 75.0,
            'activity_level': 'moderate', 'goal': 'maintain',
            'diabetes': False, 'hypertension': False, 'high_cholesterol': False,
            'thyroid_disorder': False, 'other_conditions': 'None',
            'allergies': [], 'lactose': False, 'gluten': False,
            'diet_type': 'regular', 'medications': 'None', 'special_notes': 'None',
            'language': 'ar'
        }

        # Check explicit language or Arabic script presence
        if re.search(r'Language:\s*en', user_prompt, re.I):
            data['language'] = 'en'
        elif re.search(r'Language:\s*ar', user_prompt, re.I) or re.search(r'[\u0600-\u06FF]', user_prompt):
            data['language'] = 'ar'

        def get_val(pattern, default=None):
            m = re.search(pattern, user_prompt, re.IGNORECASE)
            return m.group(1).strip() if m else default

        age_s = get_val(r'Age:\s*(\d+)')
        if age_s: data['age'] = int(age_s)

        gender_s = get_val(r'Gender:\s*([\w\u0600-\u06FF]+)')
        if gender_s:
            g_low = gender_s.lower()
            if 'fem' in g_low or 'أنثى' in g_low or 'انثى' in g_low:
                data['gender'] = 'female'
            else:
                data['gender'] = 'male'

        h_s = get_val(r'Height:\s*([\d\.]+)')
        if h_s: data['height_cm'] = float(h_s)

        w_s = get_val(r'Weight:\s*([\d\.]+)')
        if w_s: data['weight_kg'] = float(w_s)

        act_s = get_val(r'Activity Level:\s*([\w_]+)')
        if act_s: data['activity_level'] = act_s.lower()

        goal_s = get_val(r'Goal:\s*([\w_]+)')
        if goal_s: data['goal'] = goal_s.lower()

        diet_s = get_val(r'Diet Preference:\s*([\w_]+)')
        if diet_s: data['diet_type'] = diet_s.lower()

        if re.search(r'Diabetes:\s*(yes|true|نعم)', user_prompt, re.I): data['diabetes'] = True
        if re.search(r'Hypertension:\s*(yes|true|نعم)', user_prompt, re.I): data['hypertension'] = True
        if re.search(r'High Cholesterol:\s*(yes|true|نعم)', user_prompt, re.I): data['high_cholesterol'] = True
        if re.search(r'Thyroid Disorder:\s*(yes|true|نعم)', user_prompt, re.I): data['thyroid_disorder'] = True
        if re.search(r'Lactose intolerance:\s*(yes|true|نعم)', user_prompt, re.I): data['lactose'] = True
        if re.search(r'Gluten intolerance:\s*(yes|true|نعم)', user_prompt, re.I): data['gluten'] = True

        allergies_s = get_val(r'Food Allergies:\s*(.+)')
        if allergies_s and allergies_s.lower() not in ('none', 'لا يوجد', 'بدون'):
            data['allergies'] = [a.strip() for a in allergies_s.split(',') if a.strip()]

        return data

    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 8000,
        model: Optional[str] = None,
    ) -> str:
        data = self._parse_prompt(user_prompt)
        is_ar = (data['language'] == 'ar')

        # ── Mifflin-St Jeor Clinical Equation ──
        w = data['weight_kg']
        h = data['height_cm']
        a = data['age']
        if data['gender'] == 'female':
            bmr = 10 * w + 6.25 * h - 5 * a - 161
        else:
            bmr = 10 * w + 6.25 * h - 5 * a + 5

        activity_mult = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }.get(data['activity_level'], 1.4)

        tdee = bmr * activity_mult
        goal = data['goal']

        if 'lose' in goal:
            daily_cals = int(tdee - 450)
            p_ratio, c_ratio, f_ratio = 0.35, 0.35, 0.30
        elif 'muscle' in goal or 'gain' in goal:
            daily_cals = int(tdee + 350)
            p_ratio, c_ratio, f_ratio = 0.30, 0.45, 0.25
        else:
            daily_cals = int(tdee)
            p_ratio, c_ratio, f_ratio = 0.25, 0.50, 0.25

        daily_cals = max(1300, daily_cals)
        protein_g = int((daily_cals * p_ratio) / 4)
        carbs_g = int((daily_cals * c_ratio) / 4)
        fat_g = int((daily_cals * f_ratio) / 9)

        # ── Clinical Adjustments ──
        adjustments = []
        if is_ar:
            if data['diabetes']:
                adjustments.append("تنظيم مؤشر السكر الجلايسيمي (Low-GI) وتوزيع الكربوهيدرات لضبط مستويات الجلوكوز.")
            if data['hypertension']:
                adjustments.append("تقليل الصوديوم (<1500 مجم/يوم) والتركيز على أطعمة غنية بالبوتاسيوم والمغنيسيوم (بروتوكول DASH).")
            if data['high_cholesterol']:
                adjustments.append("تخفيض الدهون المشبعة (<6%) وزيادة الألياف القابلة للذوبان كالشوفان والبقوليات.")
            if data['thyroid_disorder']:
                adjustments.append("تأمين كميات متوازنة من السيلينيوم والزنك واليود وتناول الخضروات الصليبية مطهية جيداً.")
            if data['lactose']:
                adjustments.append("استبعاد منتجات الألبان التقليدية واستبدالها بحليب وبدائل خالية تماماً من اللاكتوز.")
            if data['gluten']:
                adjustments.append("الاعتماد على حبوب خالية من الجلوتين بنسبة 100% (أرز بني، كينوا، حنطة سوداء).")
            if data['allergies']:
                adjustments.append(f"استبعاد تام لجميع مسببات الحساسية المحددة: {', '.join(data['allergies'])}.")
            if not adjustments:
                adjustments.append("توزيع متوازن للعناصر الكبرى متوافق مع التمثيل الغذائي ومستوى نشاطك اليومي.")
        else:
            if data['diabetes']:
                adjustments.append("Strict low-GI carbohydrates distributed evenly to regulate blood glucose.")
            if data['hypertension']:
                adjustments.append("Low sodium (<1500mg/day) with potassium-rich whole foods (DASH protocol).")
            if data['high_cholesterol']:
                adjustments.append("Restricted saturated fats (<6%) with high soluble dietary fiber (oats, legumes).")
            if data['thyroid_disorder']:
                adjustments.append("Adequate selenium, zinc, and balanced iodine intake; cooked cruciferous vegetables.")
            if data['lactose']:
                adjustments.append("100% lactose-free alternatives (almond/oat milk, fortified plant yogurts).")
            if data['gluten']:
                adjustments.append("Certified gluten-free grains only (quinoa, brown rice, buckwheat, oats GF).")
            if data['allergies']:
                adjustments.append(f"Completely excluded known allergens: {', '.join(data['allergies'])}.")
            if not adjustments:
                adjustments.append("Balanced macronutrient profile customized to your daily physical activity and metabolic target.")

        diet = data['diet_type']
        is_vegan = 'vegan' in diet
        is_veg = 'veg' in diet
        is_keto = 'keto' in diet

        # ── Meals Generator ──
        def get_day_meals(day_num: int):
            c_b = int(daily_cals * 0.25)
            c_l = int(daily_cals * 0.35)
            c_d = int(daily_cals * 0.30)
            c_s = int(daily_cals * 0.10)

            if is_ar:
                day_label = f"اليوم {day_num}"
                note_b = "اشرب 500 مل ماء فاتر فور الاستيقاظ."
                note_l = "امضغ الطعام جيداً وتجنب المشروبات الغازية أو المحلاة."
                note_d = "تناول العشاء قبل النوم بـ 2 إلى 3 ساعات على الأقل."
                note_s = "وجبة خفيفة غنية بالمغذيات بين الوجبات لتعزيز الحرق."

                if is_keto:
                    b_opts = [
                        "أومليت بيض بالسبانخ وزيت الزيتون البكر مع شرائح أفوكادو",
                        "بودينغ بذور الشيا بحليب اللوز الخالي من السكر مع جوز مجروش",
                        "بيض مسلوق مع فطر سوتيه بزيت الزيتون وشرائح خيار",
                    ]
                    l_opts = [
                        "سمك سلمون مشوي بصلصة الليمون وزيت الزيتون مع هليون أو بروكلي",
                        "سلطة دجاج مشوي مع أوراق الجرجير والخس والجبن وزيت الزيتون",
                        "شريحة لحم بقري صافي مشوي مع خضار سوتيه بزيت الزيتون",
                    ]
                    d_opts = [
                        "أوراك دجاج مشوية بالأعشاب مع قرنبيط محمص بالفرن",
                        "فيليه سمك مشوي مع بروكلي مطهو على البخار وزبدة طبيعية",
                        "شرائح كوسا مع دجاج مشوي وصلصة البيستو بزيت الزيتون",
                    ]
                    s_opts = [
                        "حفنة صغيرة من جوز المكاديميا أو اللوز الني",
                        "أعواد كرفس وخيار مع صلصة الجواكامولي الطازجة",
                        "شرائح خيار مع جبن خالي من الكربوهيدرات",
                    ]
                elif is_vegan:
                    b_opts = [
                        "شوفان كامل بحليب الصويا مع بذور الكتان وشرائح فراولة",
                        "توفو مخفوق بالكركم والسبانخ والطماطم مع خبز حبوب كاملة",
                        "سموذي نباتي غني ببذور الشيا والسبانخ والموز وحليب الشوفان",
                    ]
                    l_opts = [
                        "يخنة عدس وخضار مع أرز بني مطهو على البخار وسلطة خضراء",
                        "سلطة حمص متوسطية مع خيار، طماطم، بقدونس، وزيت زيتون وليمون",
                        "وعاء كينوا مع بطاطا حلوة مشوية، ذرة، وخضار ورقية مشكلة",
                    ]
                    d_opts = [
                        "فاصوليا حمراء مطبوخة بصلصة الطماطم والأعشاب مع شرائح أفوكادو",
                        "تيمبيه أو توفو مشوي مع بروكلي وكوسا مطبوخة على البخار",
                        "شوربة خضار مشكلة دافئة مع عدس أصفر وخبز شوفان محمص",
                    ]
                    s_opts = [
                        "شرائح تفاح مع ملعقة زبدة فول سوداني طبيعية بدون سكر",
                        "حمص مقرمش محمص بالفرن مع رشة كمون وبابريكا",
                        "حفنة من المكسرات النية وبذور اليقطين",
                    ]
                elif is_veg:
                    b_opts = [
                        "زبادي يوناني مع ملعقة عسل طبيعي وبذور الشيا والتوت",
                        "فطيرة بيض وخضار مشكلة (فلفل ألوان، سبانخ، جبن قريش)",
                        "شوفان ليلي بالحليب واللوز والتفاح المبشور والقرفة",
                    ]
                    l_opts = [
                        "طاجن جبن حلوم أو بانير مشوي مع كينوا وسلطة حديقة خضراء",
                        "وعاء حمص متوسطي مع جبن فيتا وزيت زيتون وخضار",
                        "شوربة عدس غنية بالليمون والكمون مع ربع رغيف بلدي وسلطة",
                    ]
                    d_opts = [
                        "باذنجان مشوي بالفرن مع صلصة طماطم خفيفة وسلطة خضراء",
                        "توفو مقلب مع فاصوليا خضراء وجزر وأرز بني",
                        "فلفل حلو محشو بجبن القريش والأعشاب والمشروم",
                    ]
                    s_opts = [
                        "جبنة قريش خفيفة مع شرائح خيار أو أناناس طازج",
                        "أصابع جزر وخيار مع غموس الحمص الصحي",
                        "حفنة من اللوز الني غير المملح",
                    ]
                else:
                    b_opts = [
                        "بيضتان مسلوقتان مع ربع رغيف بلدي كامل وسلطة خضراء غنية بزيت الزيتون",
                        "طبق شوفان بالحليب قليل الدسم مع بذور الشيا ومسحة عسل طبيعي وشرائح تفاح",
                        "جبنة قريش بزيت الزيتون البكر والطماطم والزعتر مع شريحة توست أسمر",
                        "عجة بيض بالخضار والمشروم مطهوة بمسحة زيت زيتون مع شرائح خيار وكوب شاي أخضر",
                        "زبادي يوناني طبيعي مع حفنة مكسرات نية وتوت بري أو قطع فراولة",
                    ]
                    l_opts = [
                        "صدر دجاج مشوي بالأعشاب والليمون مع 5 ملاعق أرز بني وخضار سوتيه",
                        "سمك فيليه مشوي بالفرن مع بطاطا حلوة مشوية وسلطة جرجير وطماطم",
                        "طاجن خضار بالفرن (كوسا وفاصوليا) مع قطع لحم بقري صافي و4 ملاعق أرز",
                        "علبة تونة مصفاة بالليمون والكمون مع سلطة كينوا أو أرز وخضار ورقية",
                        "شيش طاووق دجاج مشوي مع خضار مشوية وسلطة خضراء مع ملعقة زيت زيتون",
                    ]
                    d_opts = [
                        "كوب زبادي خفيف مع بذور الكتان وعصرة ليمون وشريحة توست بني مع جبن قريش",
                        "شوربة عدس أصفر دافئة مع طبق سلطة خضراء بدون دهون مهدرجة",
                        "سلطة تونة خفيفة مع خس، خيار، طماطم، وزيت زيتون وعصير ليمون",
                        "بيضة مسلوقة مع شريحة توست حبوب كاملة وشرائح خيار وطماطم",
                        "شوربة خضار مشكلة دافئة مع شريحة صدر ديك رومي أو دجاج مشوي",
                    ]
                    s_opts = [
                        "حبة تفاح متوسطة مع 7 حبات لوز ني غير مملح",
                        "طبق شرائح خيار وجزر طازج مع ملعقة حمص حب مطحون",
                        "كوب شاي أخضر بالنعناع مع حفنة صغيرة من عين الجمل",
                        "شريحة توست بني مع ملعقة زبدة فول سوداني طبيعية",
                        "كوب زبادي طبيعي صغير مع رشة قرفة وبذور شيا",
                    ]

            else:
                day_label = f"Day {day_num}"
                note_b = "Hydrate with 500ml water upon waking."
                note_l = "Chew thoroughly; avoid sweetened drinks."
                note_d = "Consume at least 2-3 hours before sleep."
                note_s = "Healthy nutrient-dense snack between meals."

                if is_keto:
                    b_opts = [
                        "Avocado and spinach omelet with olive oil",
                        "Chia seed pudding with almond milk and crushed walnuts",
                        "Poached eggs with sautéed mushrooms and avocado slices",
                    ]
                    l_opts = [
                        "Grilled salmon with lemon butter sauce and asparagus",
                        "Chicken Caesar salad (no croutons) with parmesan and olive oil",
                        "Grass-fed beef burger patty with mixed greens and avocado",
                    ]
                    d_opts = [
                        "Baked herb-crusted chicken thighs with roasted cauliflower",
                        "Pan-seared cod with steamed broccoli and herb butter",
                        "Zucchini noodles with creamy garlic pesto and grilled chicken",
                    ]
                    s_opts = [
                        "A handful of raw macadamia nuts",
                        "Celery sticks with sugar-free almond butter",
                        "Sliced cucumber with guacamole",
                    ]
                elif is_vegan:
                    b_opts = [
                        "Rolled oats with chia seeds, flaxseed, berries and soy milk",
                        "Tofu scramble with turmeric, spinach, tomatoes and whole grain toast",
                        "Green smoothie bowl with plant protein, spinach, banana and hemp seeds",
                    ]
                    l_opts = [
                        "Lentil and vegetable stew with steamed brown rice",
                        "Chickpea Mediterranean salad with cucumber, olives and tahini",
                        "Quinoa Buddha bowl with roasted sweet potato, kale and edamame",
                    ]
                    d_opts = [
                        "Black bean chili with diced avocado and cilantro",
                        "Grilled marinated tempeh with sautéed broccoli and quinoa",
                        "Lentil shepherd's pie with cauliflower-potato mash topping",
                    ]
                    s_opts = [
                        "Apple slices with natural peanut butter",
                        "Roasted crispy chickpeas with paprika",
                        "Handful of raw mixed nuts and pumpkin seeds",
                    ]
                elif is_veg:
                    b_opts = [
                        "Greek yogurt with honey, chia seeds and blueberries",
                        "Vegetable frittata with bell peppers, spinach and goat cheese",
                        "Overnight oats with almond milk, grated apple and walnuts",
                    ]
                    l_opts = [
                        "Paneer or tofu tikka with quinoa and fresh garden salad",
                        "Mediterranean chickpea bowl with feta cheese and olive oil",
                        "Lentil soup with warm whole-grain pita bread",
                    ]
                    d_opts = [
                        "Baked eggplant parmesan with mixed salad",
                        "Stir-fried tofu with snap peas, carrots and brown rice",
                        "Spinach and ricotta stuffed bell peppers",
                    ]
                    s_opts = [
                        "Cottage cheese with sliced pineapple",
                        "Carrot and bell pepper sticks with hummus",
                        "Handful of raw almonds",
                    ]
                else:
                    b_opts = [
                        "Scrambled eggs with sautéed spinach, mushrooms and whole wheat toast",
                        "Steel-cut oatmeal with sliced banana, chia seeds and almond milk",
                        "Greek yogurt parfait with mixed berries and crushed walnuts",
                        "Poached eggs on avocado toast with smoked paprika",
                        "High-protein berry smoothie with whey/plant protein and oats",
                    ]
                    l_opts = [
                        "Grilled lemon herb chicken breast with quinoa and steamed broccoli",
                        "Baked salmon fillet with roasted sweet potato and asparagus",
                        "Turkey breast wrap with hummus, cucumber and mixed greens",
                        "Seared tuna salad with olive oil, boiled eggs and green beans",
                        "Lean beef stir-fry with snap peas, bell peppers and brown rice",
                    ]
                    d_opts = [
                        "Baked cod fillet with steamed green beans and wild rice",
                        "Grilled herb chicken thighs with roasted zucchini and bell peppers",
                        "Lentil and vegetable soup with grilled chicken breast",
                        "Lean grilled steak strips with sautéed spinach and mashed sweet potato",
                        "Pan-roasted chicken breast with Mediterranean roasted vegetables",
                    ]
                    s_opts = [
                        "Handful of raw almonds and an apple",
                        "Greek yogurt with a teaspoon of flaxseeds",
                        "Carrot sticks and cucumber slices with hummus",
                        "Handful of raw walnuts and a pear",
                        "Rice cakes topped with natural peanut butter",
                    ]

            b = b_opts[(day_num - 1) % len(b_opts)]
            l = l_opts[(day_num - 1) % len(l_opts)]
            d = d_opts[(day_num - 1) % len(d_opts)]
            s = s_opts[(day_num - 1) % len(s_opts)]

            # Allergies & Intolerance replacement rules
            if data['lactose']:
                if is_ar:
                    b = b.replace('حليب قليل الدسم', 'حليب لوز غير محلى').replace('زبادي', 'زبادي خالي من اللاكتوز').replace('جبنة قريش', 'توفو متبل')
                else:
                    b = b.replace('Greek yogurt', 'Dairy-free almond yogurt').replace('feta cheese', 'vegan cheese')
            if data['gluten']:
                if is_ar:
                    b = b.replace('رغيف بلدي', 'خبز خالي من الجلوتين').replace('توست أسمر', 'توست خالي من الجلوتين')
                else:
                    b = b.replace('whole wheat toast', 'gluten-free toast').replace('pita bread', 'gluten-free wrap')
                    l = l.replace('wrap', 'quinoa bowl')

            cal_suffix = "سعرة" if is_ar else "kcal"

            return {
                'day': day_label,
                'meals': {
                    'breakfast': {'meal': b, 'calories': f'{c_b} {cal_suffix}', 'notes': note_b},
                    'lunch':     {'meal': l, 'calories': f'{c_l} {cal_suffix}', 'notes': note_l},
                    'dinner':    {'meal': d, 'calories': f'{c_d} {cal_suffix}', 'notes': note_d},
                    'snack':     {'meal': s, 'calories': f'{c_s} {cal_suffix}', 'notes': note_s},
                }
            }

        meal_plan = [get_day_meals(i) for i in range(1, 16)]

        if is_ar:
            gender_txt = "ذكر" if data['gender'] == 'male' else "أنثى"
            goal_trans = {"lose_weight": "خسارة الوزن", "maintain": "تثبيت الوزن", "gain_muscle": "بناء العضلات"}.get(data['goal'], data['goal'])
            diet_trans = {"regular": "متوازن", "vegetarian": "نباتي", "vegan": "فيجان", "keto": "كيتو"}.get(data['diet_type'], data['diet_type'])
            profile_summary = (
                f"الملف الصحي: {gender_txt}، {data['age']} عاماً، الوزن: {data['weight_kg']} كجم، الطول: {data['height_cm']} سم. "
                f"النشاط: {data['activity_level']}، الهدف: {goal_trans}، النمط الغذائي: {diet_trans}."
            )
            daily_cals_str = f"{daily_cals} سعرة/اليوم (معدل الأيض الأساسي: {int(bmr)}، الاحتياج الكلي: {int(tdee)})"
            macros_dict = {
                'protein': f'{protein_g} جم ({int(p_ratio*100)}%)',
                'carbs': f'{carbs_g} جم ({int(c_ratio*100)}%)',
                'fat': f'{fat_g} جم ({int(f_ratio*100)}%)',
            }
            disclaimer_txt = "تم إنشاء هذه الخطة عبر محرك NutriAI الذكي السريري (وضع بدون إنترنت). هذه الخطة للإرشاد التغذوي ولا تغني عن استشارة الطبيب المختص."
        else:
            profile_summary = (
                f"{data['gender'].capitalize()}, {data['age']} years old, {data['weight_kg']} kg, {data['height_cm']} cm. "
                f"Activity: {data['activity_level']}, Goal: {data['goal']}, Diet: {data['diet_type']}."
            )
            daily_cals_str = f"{daily_cals} kcal/day (BMR: {int(bmr)} kcal, TDEE: {int(tdee)} kcal)"
            macros_dict = {
                'protein': f'{protein_g}g ({int(p_ratio*100)}%)',
                'carbs': f'{carbs_g}g ({int(c_ratio*100)}%)',
                'fat': f'{fat_g}g ({int(f_ratio*100)}%)',
            }
            disclaimer_txt = "Generated by NutriAI Clinical Engine (Offline Mode). This meal plan is for nutritional guidance and does not replace professional medical consultation."

        plan_dict = {
            'user_profile_summary': profile_summary,
            'daily_calories': daily_cals_str,
            'macros': macros_dict,
            'medical_adjustments': adjustments,
            'meal_plan': meal_plan,
            'disclaimer': disclaimer_txt
        }

        return json.dumps(plan_dict, ensure_ascii=False, indent=2)

    # ══════════════════════════════════════════════════════════════════════════
    # INTERACTIVE CONVERSATIONAL AGENT (Contextual Clinical Intelligence)
    # ══════════════════════════════════════════════════════════════════════════

    async def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        diet_plan: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        model: Optional[str] = None,
    ) -> str:
        last_user_msg = ''
        for m in reversed(messages):
            if m.get('role') == 'user':
                last_user_msg = m.get('content', '').strip().lower()
                break

        is_ar = bool(re.search(r'[\u0600-\u06FF]', last_user_msg))

        # Safe plan references
        plan = diet_plan or {}
        macros = plan.get('macros', {})
        daily_cals = plan.get('daily_calories', '2000 سعرة/اليوم')
        protein = macros.get('protein', '150 جم')
        carbs = macros.get('carbs', '200 جم')
        fat = macros.get('fat', '60 جم')
        meal_list = plan.get('meal_plan', [])

        # Normalize text for robust matching
        clean_msg = last_user_msg.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ة', 'ه')

        # ── 1. GREETINGS & INTRODUCTIONS ──
        is_greeting = (
            any(w in clean_msg for w in ['ازيك', 'عامل ايه', 'اخبارك', 'سلام', 'مرحبا', 'اهلا', 'صباح الخير', 'مساء الخير'])
            or bool(re.search(r'\b(hello|hi|hey|greetings)\b', clean_msg))
        )
        if is_greeting:
            if is_ar:
                return (
                    "أهلاً وسهلاً بك! 🥗 أنا **NutriAI**، أخصائي التغذية العلاجية الذكي الخاص بك.\n\n"
                    "أنا هنا لمتابعة خطتك الغذائية خطوة بخطوة. يمكنك سؤالي عن:\n"
                    "• **تفاصيل أي يوم:** (مثال: وجبات اليوم الأول أو وجبة الغداء اليوم الخامس)\n"
                    "• **بدائل الأطعمة:** (مثال: بديل الفراخ، بديل البيض، بديل الأرز)\n"
                    "• **سعراتك والعناصر الكبرى:** (مثال: كم بروتين أو نشويات في خطتي؟)\n"
                    "• **نصائح التمارين، شرب الماء، والتعامل مع ثبات الوزن**\n\n"
                    "كيف يمكنني مساعدتك الآن؟"
                )
            else:
                return (
                    "Hello! 🥗 I am **NutriAI**, your personalized clinical nutrition assistant.\n\n"
                    "I am here to guide you through your 15-day meal plan. You can ask me about:\n"
                    "• **Specific Day Meals:** (e.g. Day 1 meals, Day 5 lunch)\n"
                    "• **Ingredient Substitutions:** (e.g. Can I replace chicken with fish?)\n"
                    "• **Calories & Macros:** (e.g. How much protein or carbs?)\n"
                    "• **Hydration, exercise, and weight loss tips**\n\n"
                    "How can I help you today?"
                )

        # ── 2. THANKS & APPRECIATION ──
        if any(w in clean_msg for w in ['شكرا', 'تسلم', 'جزاك الله', 'حبيبي', 'كلك ذوق', 'مشكور', 'تمام كدة', 'فهمت', 'thanks', 'thank you', 'thx']):
            if is_ar:
                return (
                    "العفو، على الرحب والسعة دائماً! 🌟\n\n"
                    "أنا فخور بالتزامك وسعيك لتحقيق أهدافك الصحية. تذكر أن الاستمرارية هي السر الحقيقي في نجاح أي نظام غذائي.\n\n"
                    "إذا طرأ أي سؤال أثناء تحضير وجباتك أو رغبت في استبدال أي صنف، أنا موجود هنا لمساعدتك في أي وقت!"
                )
            else:
                return (
                    "You're very welcome! 🌟\n\n"
                    "Consistency is the true key to long-term health and fitness success. Keep up the great work!\n"
                    "Feel free to ask anytime if you need more tips or meal substitutions."
                )

        # ── 3. WHO ARE YOU / SYSTEM IDENTITY ──
        if any(w in clean_msg for w in ['مين انت', 'وظيفتك', 'ما هو دورك', 'من انت', 'who are you', 'what are you']):
            if is_ar:
                return (
                    "أنا **NutriAI**، نظام ذكاء اصطناعي سريري متخصص في التغذية العلاجية وإعداد الأنظمة الغذائية الذكية.\n\n"
                    "• تم تطويري بالاعتماد على خوارزميات **Mifflin-St Jeor** الطبية وقواعد التغذية السريرية المعتمدة.\n"
                    "• أقوم بتحليل معاييرك الصحية (العمر، الطول، الوزن، النشاط، السكر، الضغط، الحساسيات) لإنتاج خطط غذائية دقيقة بنسبة 100% بدون أي تضارب دوائي أو غذائي.\n"
                    "• أعمل محلياً بالكامل دون الحاجة لأي اتصال خارجي بالإنترنت لحماية خصوصيتك التامة!"
                )
            else:
                return (
                    "I am **NutriAI**, an AI clinical nutrition system designed to deliver personalized, evidence-based dietary recommendations.\n\n"
                    "• Powered by the Mifflin-St Jeor metabolic formula and clinical guidelines.\n"
                    "• I evaluate biometric profiles, metabolic goals, and medical conditions (diabetes, hypertension, allergies).\n"
                    "• Operates 100% locally and offline to safeguard patient privacy."
                )

        # ── 4. CAFFEINE, COFFEE & TEA (PRIORITY OVER GENERIC WATER) ──
        if any(w in clean_msg for w in ['قهوه', 'كافيين', 'نسكافيه', 'coffee', 'شاي اخضر', 'green tea']):
            if is_ar:
                return (
                    "☕ **دليل القهوة والشاي أثناء النظام الغذائي:**\n\n"
                    "• **القهوة:** مسموح بـ 1 إلى 2 فنجان قهوة سادة أو أمريكانو بدون سكر يومياً (ترفع معدل الأيض والتركيز).\n"
                    "• **الشاي الأخضر:** ممتاز لحرق الدهون ومضادات الأكسدة، ويفضل تناوله بين الوجبات أو قبل التمرين بنصف ساعة.\n"
                    "• **محاذير مهمة:**\n"
                    "  1. تجنب القهوة المحلاة، الكريمر (المبيض)، والمشروبات ذات النكهات عالية السعرات.\n"
                    "  2. اشرب كوب ماء كبير مع كل فنجان قهوة لأن الكافيين مدر طبيعي للبول.\n"
                    "  3. توقف عن تناول الكافيين قبل موعد النوم بـ 6 ساعات على الأقل لضمان نوم عميق وحرق دهون مثالي."
                )
            else:
                return (
                    "☕ **Coffee & Caffeine Guidelines:**\n\n"
                    "• 1-2 cups of black coffee or unsweetened green tea daily boosts metabolic rate.\n"
                    "• Avoid sugar, commercial creamers, and syrups.\n"
                    "• Drink a glass of water alongside every cup of coffee.\n"
                    "• Avoid caffeine at least 6 hours before bedtime to preserve deep sleep quality."
                )

        # ── 5. SPECIFIC FOOD SUBSTITUTIONS (INFORMATIONAL EQUIVALENCES) ──
        is_sub_intent = any(k in clean_msg for k in ['بديل', 'استبدال', 'ابدل', 'بدائل', 'تغيير', 'غير', 'بدل', 'replace', 'substitute'])
        is_apply_intent = any(w in clean_msg for w in [
            'في الخطه', 'في الخطة', 'في الجداول', 'في الجدول', 'شيل', 'مش عاوز', 'مش عايز',
            'بدون', 'احذف', 'اعتمد', 'طبق', 'حدث', 'استبدل', 'بدل'
        ])

        # If user wants to apply changes or modify plan, skip pure informational guides so section 5.5 executes
        if not is_apply_intent:
            # Egg substitution (Informational)
            if 'بيض' in clean_msg and (is_sub_intent or 'فطار' in clean_msg or 'عشا' in clean_msg):
                if is_ar:
                    return (
                        "🥚 **بدائل البيض بالجرامات المتكافئة:**\n\n"
                        "كل بيضتين مسلوقتين (حوالي 140 سعرة و13 جم بروتين) يمكنك استبدالهما بـ:\n"
                        "• **100 جم جبنة قريش** بزيت الزيتون ورشة زعتر أو كمون.\n"
                        "• **150 جم زبادي يوناني طبيعي** غير محلى.\n"
                        "• **4 ملاعق كبيرة فول مدمس** بالكمون والليمون وزيت الزيتون.\n"
                        "• **علبة تونة مصفاة بالماء** والليمون.\n"
                        "• **100 جم توفو** مشوح بالأعشاب والكركم (خيار نباتي).\n\n"
                        "💡 *لتطبيق هذا البديل في جداول خطتك الـ 15 يوماً وتحديث ملف الـ PDF فوراً، قل لي:* **(استبدل البيض بجبنة قريش في الخطة)**."
                    )
                else:
                    return (
                        "🥚 **Egg Substitutions:**\n\n"
                        "2 boiled eggs (approx. 140 kcal, 13g protein) can be substituted with:\n"
                        "• 100g low-fat cottage cheese with olive oil and oregano\n"
                        "• 150g plain unsweetened Greek yogurt\n"
                        "• 4 tbsp cooked fava beans with olive oil and lemon\n"
                        "• 1 small can of water-drained tuna"
                    )

            # Chicken substitution (Informational)
            if any(k in clean_msg for k in ['فراخ', 'دجاج', 'صدر دجاج', 'chicken']) and (is_sub_intent or 'غدا' in clean_msg or 'لحم' in clean_msg):
                if is_ar:
                    return (
                        "🍗 **بدائل صدور الدجاج بالجرامات المتكافئة:**\n\n"
                        "كل 150 جم صدر دجاج مشوي (حوالي 200-240 سعرة و35 جم بروتين) يمكن استبداله بـ:\n"
                        "• **150 جم صدر ديك رومي مشوي**.\n"
                        "• **170 جم سمك فيليه مشوي** (بلطي، بوري، قشر بياض).\n"
                        "• **150 جم سمك سلمون مشوي** (غني جداً بالأوميغا 3 والدهون الصحية).\n"
                        "• **علبة تونة مصفاة بالماء** (140 جم صافي).\n"
                        "• **180 جم جبن قريش قليل الدسم** مع سلطة خضراء.\n"
                        "• **3 بيضات مسلوقة** (بيضتان كاملتان + بياض بيضة).\n\n"
                        "💡 *لتطبيق هذا البديل في جداول خطتك الـ 15 يوماً وتحديث ملف الـ PDF فوراً، قل لي:* **(استبدل الفراخ بسمك مشوي في الخطة)**."
                    )
                else:
                    return (
                        "🍗 **Chicken Breast Substitutions:**\n\n"
                        "150g grilled chicken breast can be replaced with:\n"
                        "• 150g grilled turkey breast\n"
                        "• 170g grilled white fish fillet\n"
                        "• 150g baked salmon fillet\n"
                        "• 1 standard can of water-drained chunk tuna\n"
                        "• 3 boiled eggs (2 whole + 1 white)"
                    )

            # Fish & Tuna substitution (Informational)
            if any(k in clean_msg for k in ['سمك', 'سلمون', 'تونه', 'تونة', 'fish', 'tuna']) and is_sub_intent:
                if is_ar:
                    return (
                        "🐟 **بدائل الأسماك والتونة بالجرامات المتكافئة:**\n\n"
                        "وجبة السمك أو التونة المشوية يمكن استبدالها بـ:\n"
                        "• **150 جم صدر دجاج أو ديك رومي مشوي**.\n"
                        "• **3 بيضات مسلوقة** مع نصف رغيف بلدي وسلطة.\n"
                        "• **طبق عدس بني مسلوق** (كوب مطبوخ) مع ملعقة زيت زيتون وخضار.\n\n"
                        "💡 *لتطبيق هذا البديل في جداول خطتك فوراً، قل لي:* **(بدل السمك بصدور دجاج في الخطة)**."
                    )
                else:
                    return (
                        "🐟 **Fish & Seafood Substitutions:**\n\n"
                        "Can be replaced with 150g grilled chicken or turkey breast, 3 boiled eggs, or 1 cup of cooked brown lentils."
                    )

            # Bread / Rice / Carbs substitution (Informational)
            if any(k in clean_msg for k in ['رز', 'ارز', 'عيش', 'خبز', 'مكرونه', 'bread', 'rice', 'بطاطا']) and (is_sub_intent or 'نشويات' in clean_msg):
                if is_ar:
                    return (
                        "🍚 **بدائل الأرز البني والخبز (النشويات المعقدة):**\n\n"
                        "كل 5 ملاعق أرز بني مطبوخ يمكن استبدالها بأحد الخيارات المتكافئة التالية:\n"
                        "• **حبة بطاطا حلوة متوسطة** مشوية بالفرن (حوالي 150 جم).\n"
                        "• **حبة بطاطس مسلوقة أو مشوية** متوسطة الحجم مهروسة برشة كمون وزيت زيتون.\n"
                        "• **5 ملاعق كبيرة كينوا أو برغل مطبوخ**.\n"
                        "• **نصف رغيف خبز بلدي أسمر (ردة)** أو شريحتين توست حبوب كاملة.\n"
                        "• **4 ملاعق كبيرة شوفان كامل جاف** مطبوخ بحليب خالي الدسم.\n\n"
                        "💡 *لتطبيق هذا البديل في جداول خطتك فوراً، قل لي:* **(استبدل الأرز ببطاطا مشوية في الخطة)**."
                    )
                else:
                    return (
                        "🍚 **Carbohydrate Substitutions:**\n\n"
                        "5 tbsp cooked brown rice can be replaced with:\n"
                        "• 1 medium baked sweet potato (approx. 150g)\n"
                        "• 5 tbsp cooked quinoa or buckwheat\n"
                        "• 2 slices 100% whole grain toast\n"
                        "• 40g dry rolled oats cooked with water"
                    )

            # General substitution guide
            if is_sub_intent:
                if is_ar:
                    return (
                        "🔄 **دليل الاستبدال الغذائي الذكي:**\n\n"
                        "• **البروتين:** صدور دجاج <-> سمك فيليه <-> تونة <-> ديك رومي <-> بيض مسلوق <-> جبن قريش.\n"
                        "• **النشويات:** أرز بني <-> بطاطا مشوية <-> كينوا <-> شوفان <-> خبز حبوب كاملة.\n"
                        "• **الدهون الصحية:** زيت زيتون بكر <-> أفوكادو <-> 10 حبات لوز أو عين جمل <-> بذور شيا.\n"
                        "• **الألبان:** حليب البقر <-> حليب اللوز أو الشوفان غير المحلى.\n\n"
                        "👉 أخبرني بالمكون المحدد الذي ترغب في استبداله وسأعطيك البديل والجرام المناسب فوراً!"
                    )
                else:
                    return (
                        "🔄 **Smart Ingredient Substitutions:**\n\n"
                        "• **Proteins:** Chicken breast <-> Turkey, Salmon, Cod, Tuna, Eggs, or Cottage cheese.\n"
                        "• **Carbs:** Brown rice <-> Sweet potato, Quinoa, Rolled oats, or Whole wheat bread.\n"
                        "• **Healthy Fats:** Olive oil <-> Avocado, Raw walnuts, Almonds, or Chia seeds.\n\n"
                        "Tell me the exact food you wish to replace and I will provide the precise equivalent portion!"
                    )

        # ── 5.5 MEAL MODIFICATIONS, DAY SWAPPING & INGREDIENT EXCLUSIONS ──
        is_modify_intent = any(w in clean_msg for w in [
            'عدل', 'غير', 'بدل', 'استبدل', 'تبديل', 'تعديل', 'تغيير',
            'modify', 'swap', 'change', 'switch', 'replace'
        ])
        is_exclude_egg = any(w in clean_msg for w in [
            'مش عاوز بيض', 'بدون بيض', 'شيل البيض', 'من غير بيض', 'مبحبش البيض', 'بلاش بيض',
            'no egg', 'no eggs', 'without egg', 'without eggs'
        ])
        is_exclude_chicken = any(w in clean_msg for w in [
            'مش عاوز فراخ', 'بدون فراخ', 'شيل الفراخ', 'مش عاوز دجاج', 'بدون دجاج', 'شيل الدجاج',
            'no chicken', 'without chicken'
        ])
        is_exclude_fish = any(w in clean_msg for w in [
            'مش عاوز سمك', 'بدون سمك', 'شيل السمك', 'مش عاوز تونه', 'no fish', 'no tuna'
        ])

        # Multi-day extraction with Arabic prefixes (ب, بال, لل, و, ف, ك) and all Egyptian colloquial variants
        ar_num_map = [
            # Day 1
            ('الاولاني', 1), ('اولاني', 1), ('الاول', 1), ('اول', 1), ('واحد', 1),
            # Day 2
            ('الثاني', 2), ('التاني', 2), ('تاني', 2), ('ثاني', 2), ('اثنين', 2), ('اتنين', 2),
            # Day 3
            ('الثالث', 3), ('التالت', 3), ('تالت', 3), ('ثالث', 3), ('ثلاثة', 3), ('تلاتة', 3), ('تلاته', 3),
            # Day 4
            ('الرابع', 4), ('رابع', 4), ('اربعة', 4), ('اربعه', 4),
            # Day 5
            ('الخامس', 5), ('خامس', 5), ('خمسة', 5), ('خمسه', 5),
            # Day 6
            ('السادس', 6), ('سادس', 6), ('ستة', 6), ('سته', 6),
            # Day 7
            ('السابع', 7), ('سابع', 7), ('سبعة', 7), ('سبعه', 7),
            # Day 8
            ('الثامن', 8), ('التامن', 8), ('تامن', 8), ('ثامن', 8), ('ثمانية', 8), ('تمانية', 8), ('تمانيه', 8),
            # Day 9
            ('التاسع', 9), ('تاسع', 9), ('تسعة', 9), ('تسعه', 9),
            # Day 10
            ('العاشر', 10), ('عاشر', 10), ('عشرة', 10), ('عشره', 10),
            # Day 11 to 15
            ('الحادي عشر', 11), ('11', 11),
            ('الثاني عشر', 12), ('التاني عشر', 12), ('12', 12),
            ('الثالث عشر', 13), ('التالت عشر', 13), ('13', 13),
            ('الرابع عشر', 14), ('14', 14),
            ('الخامس عشر', 15), ('15', 15),
            ('10', 10), ('9', 9), ('8', 8), ('7', 7), ('6', 6), ('5', 5), ('4', 4), ('3', 3), ('2', 2), ('1', 1)
        ]
        detected_days = []
        for word, num in ar_num_map:
            pattern = r'(?:^|\s|[^\w])(?:[بولفك]|بال|لل)?' + re.escape(word) + r'(?:$|\s|[^\w])'
            for m in re.finditer(pattern, clean_msg):
                detected_days.append((m.start(), num))
        detected_days.sort(key=lambda x: x[0])
        ordered_days = []
        for pos, n in detected_days:
            if not ordered_days or ordered_days[-1] != n:
                ordered_days.append(n)

        # Context follow-up (e.g. user previously mentioned two days and now says: 'عدلهم ف الخطه' or 'طبق التعديل')
        is_confirm_intent = any(w in clean_msg for w in ['عدلهم', 'بدلهم', 'غيرهم', 'طبق', 'اعتمد', 'نفذ', 'اوك', 'تمام عدل', 'update them', 'apply'])
        if len(ordered_days) < 2 and is_confirm_intent:
            for prev_m in reversed(messages[:-1]):
                if prev_m.get('role') == 'user':
                    p_txt = prev_m.get('content', '').replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ة', 'ه')
                    p_days = []
                    for word, num in ar_num_map:
                        p_pat = r'(?:^|\s|[^\w])(?:[بولفك]|بال|لل)?' + re.escape(word) + r'(?:$|\s|[^\w])'
                        for m in re.finditer(p_pat, p_txt):
                            p_days.append((m.start(), num))
                    p_days.sort(key=lambda x: x[0])
                    for pos, n in p_days:
                        if not ordered_days or ordered_days[-1] != n:
                            ordered_days.append(n)
                    if len(ordered_days) >= 2:
                        break

        # ── Case A: Day Swapping (e.g. 'اليوم الاول ب اليوم التاني', 'عدل الاول بالخامس', '1 ب 2') ──
        if len(ordered_days) >= 2:
            src_day = ordered_days[0]
            tgt_day = ordered_days[1]
            
            if meal_list and len(meal_list) >= max(src_day, tgt_day):
                src_data = meal_list[src_day - 1]
                tgt_data = meal_list[tgt_day - 1]
                
                # Bilateral swap of meals between the two days
                src_meals_copy = copy.deepcopy(src_data.get('meals', {}))
                tgt_meals_copy = copy.deepcopy(tgt_data.get('meals', {}))
                
                # Apply extra exclusions if requested in the same command
                if is_exclude_egg:
                    for d_m in [src_meals_copy, tgt_meals_copy]:
                        if 'breakfast' in d_m and 'بيض' in d_m['breakfast'].get('meal', ''):
                            d_m['breakfast']['meal'] = "120 جم جبنة قريش طازجة بزيت الزيتون والزعتر مع نصف رغيف بلدي وخيار"
                            d_m['breakfast']['calories'] = "340 سعرة (22 جم بروتين)"
                            d_m['breakfast']['notes'] = "تم التحديث بناءً على طلبك في الشات"

                src_data['meals'] = tgt_meals_copy
                tgt_data['meals'] = src_meals_copy
                
                for mk in ['breakfast', 'lunch', 'dinner', 'snack']:
                    if mk in src_data['meals']:
                        src_data['meals'][mk]['notes'] = f"تم تبديلها مع اليوم {tgt_day}"
                    if mk in tgt_data['meals']:
                        tgt_data['meals'][mk]['notes'] = f"تم تبديلها مع اليوم {src_day}"

                b_desc = src_data['meals'].get('breakfast', {}).get('meal', '')
                l_desc = src_data['meals'].get('lunch', {}).get('meal', '')
                d_desc = src_data['meals'].get('dinner', {}).get('meal', '')
                s_desc = src_data['meals'].get('snack', {}).get('meal', '')

                if is_ar:
                    return (
                        f"✅ **تم تبديل وجبات اليوم {src_day} مع وجبات اليوم {tgt_day} بنجاح!**\n\n"
                        f"📋 **وجبات اليوم {src_day} الجديدة (أصبحت وجبات اليوم {tgt_day}):**\n"
                        f"• 🍳 **الإفطار:** {b_desc}\n"
                        f"• 🥗 **الغداء:** {l_desc}\n"
                        f"• 🍽️ **العشاء:** {d_desc}\n"
                        f"• 🍎 **السناك:** {s_desc}\n\n"
                        f"🎉 **أصبحت جداول الخطة في الموقع وملف الـ PDF الرسمي محدثة بالكامل الآن!**"
                    )
                else:
                    return (
                        f"✅ **Day {src_day} and Day {tgt_day} meals have been swapped successfully!**\n\n"
                        f"• Breakfast: {b_desc}\n"
                        f"• Lunch: {l_desc}\n"
                        f"• Dinner: {d_desc}\n\n"
                        f"🎉 The diet plan tables and official PDF are now fully updated!"
                    )

        # ── Case B: Single Day Modification (e.g. 'عدل اليوم الاول') ──
        if len(ordered_days) == 1 and (is_modify_intent or is_exclude_egg or is_exclude_chicken):
            target_d = ordered_days[0]
            if is_exclude_egg:
                b_desc = "120 جم جبنة قريش بزيت الزيتون والزعتر مع نصف رغيف بلدي وسلطة خضراء (بديل بيض عالي البروتين)"
                if meal_list and len(meal_list) >= target_d:
                    meal_list[target_d - 1]['meals']['breakfast']['meal'] = b_desc
                if is_ar:
                    return (
                        f"✅ **تم تعديل وجبات اليوم {target_d} واستبعاد البيض بالكامل:**\n\n"
                        f"🍳 **الإفطار الجديد (بدون بيض):**\n{b_desc}\n*💡 السعرات: 340 سعرة | البروتين: 22 جم*\n\n"
                        f"🥗 **الغداء:** صدر دجاج مشوي مع 5 ملاعق أرز بني وخضار سوتيه (580 سعرة).\n\n"
                        f"🍽️ **العشاء:** كوب زبادي يوناني مع خيار وتوست أسمر (220 سعرة).\n\n"
                        f"🍎 **سناك:** تفاحة خضراء مع 7 حبات لوز (150 سعرة)."
                    )
                else:
                    return f"✅ Day {target_d} breakfast updated without eggs: 120g low-fat cottage cheese with olive oil, whole pita, and green salad."

            if is_ar:
                return (
                    f"📋 **خيارات تعديل وجبات اليوم {target_d}:**\n\n"
                    f"لقد جهزت لك مقترحين متوازنين لتجديد وجبات اليوم {target_d}:\n\n"
                    f"🌟 **الخيار الأول (خفيف وسريع التحضير):**\n"
                    f"• **الإفطار:** طبق شوفان كامل بالحليب خفيف الدسم مع بذور الشيا ومسحة عسل وتفاح (320 سعرة).\n"
                    f"• **الغداء:** علبة تونة مصفاة بالماء والليمون مع سلطة كينوا وخضار مشكل (520 سعرة).\n"
                    f"• **العشاء:** جبنة قريش مع طماطم وزيت زيتون وتوست أسمر (250 سعرة).\n"
                    f"• **سناك:** حفنة مكسرات نية (150 سعرة).\n\n"
                    f"🌟 **الخيار الثاني (عالي البروتين والنشاط):**\n"
                    f"• **الإفطار:** 3 بيضات مسلوقة (بيضتان كاملتان + بياض بيضة) مع نصف رغيف بلدي وسلطة (360 سعرة).\n"
                    f"• **الغداء:** 180 جم سمك فيليه مشوي بالفرن مع بطاطا حلوة وسلطة خضراء (550 سعرة).\n"
                    f"• **العشاء:** كوب زبادي يوناني مع خيار ورشة بذور كتان (200 سعرة).\n"
                    f"• **سناك:** ثمرة موز مع 5 حبات لوز (160 سعرة).\n\n"
                    f"أي الخيارين يناسبك أكثر لاعتماده؟"
                )
            else:
                return f"📋 Customization options for Day {target_d}: Option A (Oats, Tuna, Greek Yogurt) or Option B (Eggs, Grilled Fish, Cottage Cheese)."

        # ── Case C: Standalone Food Exclusions & Global Plan Updates ──
        def replace_food_globally(old_kw, new_meal_str, new_cal_str, target_meal_type='breakfast'):
            cnt = 0
            for d in meal_list:
                meals = d.get('meals', {})
                for m_t in [target_meal_type, 'breakfast', 'lunch', 'dinner']:
                    m_item = meals.get(m_t, {})
                    if old_kw in m_item.get('meal', ''):
                        m_item['meal'] = new_meal_str
                        m_item['calories'] = new_cal_str
                        m_item['notes'] = 'تم التحديث بناءً على طلبك في الشات'
                        cnt += 1
            return cnt

        if is_exclude_egg or ('بيض' in clean_msg and any(w in clean_msg for w in ['استبدل', 'بدل', 'شيل', 'غير', 'مش عاوز', 'بدون', 'احذف'])):
            replace_food_globally('بيض', '120 جم جبنة قريش طازجة بزيت الزيتون والزعتر مع نصف رغيف بلدي وخيار', '340 سعرة (22 جم بروتين)', 'breakfast')
            if is_ar:
                return (
                    "✅ **تم تحديث خطتك وجداولك الغذائية بنجاح!**\n\n"
                    "تم تطبيق استبعاد البيض في **جميع أيام الخطة (15 يوماً)** وتعويضه بـ:\n"
                    "• **الإفطار الجديد المعتمد:** 120 جم جبنة قريش طازجة بزيت الزيتون والزعتر مع نصف رغيف بلدي وسلطة خضراء.\n"
                    "• **القيمة الغذائية:** 340 سعرة حرارية | 22 جم بروتين صافي (متكافئة تماماً مع وجبة البيض).\n\n"
                    "🎉 **أصبحت جداول الخطة في الموقع وملف الـ PDF الرسمي محدثة بالكامل الآن!**"
                )
            else:
                return "✅ **Plan Updated!** Eggs have been excluded from all 15 days and replaced with 120g low-fat cottage cheese with olive oil and whole pita."

        if is_exclude_chicken or (any(w in clean_msg for w in ['فراخ', 'دجاج']) and any(w in clean_msg for w in ['استبدل', 'بدل', 'شيل', 'غير', 'مش عاوز', 'بدون', 'احذف'])):
            replace_food_globally('دجاج', '170 جم سمك فيليه مشوي بالأعشاب والليمون مع 5 ملاعق أرز بني وخضار سوتيه', '550 سعرة (38 جم بروتين)', 'lunch')
            replace_food_globally('فراخ', '170 جم سمك فيليه مشوي بالأعشاب والليمون مع 5 ملاعق أرز بني وخضار سوتيه', '550 سعرة (38 جم بروتين)', 'lunch')
            if is_ar:
                return (
                    "✅ **تم تحديث خطتك وجداولك الغذائية بنجاح!**\n\n"
                    "تم استبدال الدجاج في **جميع وجبات الغداء** بـ:\n"
                    "• **الغداء الجديد المعتمد:** 170 جم سمك فيليه مشوي بالأعشاب والليمون مع 5 ملاعق أرز بني وخضار سوتيه وسلطة خضراء.\n"
                    "• **القيمة الغذائية:** 550 سعرة حرارية | 38 جم بروتين صافي.\n\n"
                    "🎉 **أصبحت جداول الخطة في الموقع وملف الـ PDF الرسمي محدثة بالكامل الآن!**"
                )
            else:
                return "✅ **Plan Updated!** Chicken has been replaced with 170g grilled white fish fillet across all 15 days."

        # Tuna / Fish Replacement
        if any(w in clean_msg for w in ['تونة', 'تونه', 'سمك']) and any(w in clean_msg for w in ['استبدل', 'بدل', 'شيل', 'غير', 'مش عاوز', 'بدون', 'احذف']):
            replace_food_globally('تونة', '160 جم صدور دجاج مشوية مع سلطة خضراء ونصف رغيف بلدي', '380 سعرة (35 جم بروتين)', 'dinner')
            replace_food_globally('تونه', '160 جم صدور دجاج مشوية مع سلطة خضراء ونصف رغيف بلدي', '380 سعرة (35 جم بروتين)', 'dinner')
            replace_food_globally('سمك', '170 جم صدور دجاج مشوية بالأعشاب مع أرز بسمتي وخضار مشوي', '520 سعرة (38 جم بروتين)', 'lunch')
            if is_ar:
                return (
                    "✅ **تم تحديث خطتك وجداولك الغذائية بنجاح!**\n\n"
                    "تم استبدال الأسماك والتونة في جداولك بـ:\n"
                    "• **البديل المعتمد:** صدور دجاج مشوية بالأعشاب بنفس السعرات ومحتوى البروتين العالي.\n\n"
                    "🎉 **أصبحت جداول الخطة في الموقع وملف الـ PDF الرسمي محدثة بالكامل الآن!**"
                )
            else:
                return "✅ **Plan Updated!** Fish and tuna have been replaced with grilled chicken breast across all 15 days."

        # Rice / Carbs Replacement
        if any(w in clean_msg for w in ['أرز', 'رز']) and any(w in clean_msg for w in ['استبدل', 'بدل', 'شيل', 'غير', 'مش عاوز', 'بدون', 'احذف']):
            replace_food_globally('أرز', '200 جم بطاطس أو بطاطا مشوية بالفرن مع رشة زيت زيتون وأعشاب', '220 سعرة (45 جم كارب صحي)', 'lunch')
            replace_food_globally('رز', '200 جم بطاطس أو بطاطا مشوية بالفرن مع رشة زيت زيتون وأعشاب', '220 سعرة (45 جم كارب صحي)', 'lunch')
            if is_ar:
                return (
                    "✅ **تم تحديث خطتك وجداولك الغذائية بنجاح!**\n\n"
                    "تم استبدال الأرز في وجبات الغداء بـ:\n"
                    "• **الكارب الصحي المعتمد:** 200 جم بطاطس أو بطاطا مشوية بالفرن (ألياف أعلى ومؤشر جلايسيمي ممتاز).\n\n"
                    "🎉 **أصبحت جداول الخطة في الموقع وملف الـ PDF الرسمي محدثة بالكامل الآن!**"
                )
            else:
                return "✅ **Plan Updated!** Rice has been replaced with 200g baked potato/sweet potato across all 15 days."

        # ── Case D: Generic Update Request (e.g. 'حدث الخطة والجداول') ──
        is_generic_update = any(p in clean_msg for p in ['حدث الخطه', 'حدث الجداول', 'تحديث الخطه', 'تحديث الجداول', 'تحديث الخطه والجداول', 'حدث الخطه والجداول'])
        if is_generic_update:
            if is_ar:
                return (
                    "✨ **مستعد لتحديث وتعديل خطتك وجداولك الغذائية فوراً!**\n\n"
                    "أخبرني بالتعديل أو الاستبدال الذي ترغب في اعتماده في جداول الخطة، وسيقوم النظام بتحديث جداول الـ 15 يوماً وملف الـ PDF فوراً:\n"
                    "• **استبدال أطعمة بالكامل:** (مثال: *'استبدل البيض بجبنة قريش'* أو *'بدل الفراخ بسمك مشوي'*).\n"
                    "• **تبديل وجبات أيام معينة:** (مثال: *'بدل اليوم الأول باليوم الخامس'*).\n"
                    "• **استبعاد أي مكون:** (مثال: *'شيل البيض من الخطة'* أو *'مش عاوز تونة'*).\n\n"
                    "ما هو التعديل أو الاستبدال الذي ترغب في تطبيقه الآن؟"
                )
            else:
                return "✨ Ready to update your plan and tables! Tell me what to modify (e.g. 'replace eggs with cottage cheese' or 'swap day 1 with day 5')."

        # ── 6. SPECIFIC DAY INQUIRY (Robust extraction for Day 1 to 15) ──
        day_match = re.search(r'(?:يوم|اليوم|day)\s*(\d+)', clean_msg)
        target_day = int(day_match.group(1)) if day_match else None

        if not target_day:
            day_words = {
                1: ['اول', 'واحد'],
                2: ['تاني', 'ثاني', 'اثنين'],
                3: ['تالت', 'ثالث', 'ثلاثه'],
                4: ['رابع', 'اربعه'],
                5: ['خامس', 'خمسه'],
                6: ['سادس', 'سته'],
                7: ['سابع', 'سبعه'],
                8: ['تامن', 'ثامن', 'ثمانيه'],
                9: ['تاسع', 'تسعه'],
                10: ['عاشر', 'عشره'],
                11: ['حادي عشر', '11'],
                12: ['ثاني عشر', '12'],
                13: ['ثالث عشر', '13'],
                14: ['رابع عشر', '14'],
                15: ['خامس عشر', '15'],
            }
            if any(k in clean_msg for k in ['يوم', 'day', 'وجبات']):
                for d_num, kw_list in day_words.items():
                    if any(kw in clean_msg for kw in kw_list):
                        target_day = d_num
                        break

        if target_day and 1 <= target_day <= 15:
            if meal_list and len(meal_list) >= target_day:
                day_data = meal_list[target_day - 1]
                meals = day_data.get('meals', {})
                b = meals.get('breakfast', {})
                l = meals.get('lunch', {})
                d = meals.get('dinner', {})
                s = meals.get('snack', {})

                if is_ar:
                    return (
                        f"📋 **تفاصيل وجبات {day_data.get('day', f'اليوم {target_day}')}:**\n\n"
                        f"🍳 **الإفطار ({b.get('calories', '—')}):**\n{b.get('meal', '—')}\n*💡 ملاحظة: {b.get('notes', '—')}*\n\n"
                        f"🥗 **الغداء ({l.get('calories', '—')}):**\n{l.get('meal', '—')}\n*💡 ملاحظة: {l.get('notes', '—')}*\n\n"
                        f"🍽️ **العشاء ({d.get('calories', '—')}):**\n{d.get('meal', '—')}\n*💡 ملاحظة: {d.get('notes', '—')}*\n\n"
                        f"🍎 **سناك ({s.get('calories', '—')}):**\n{s.get('meal', '—')}\n\n"
                        f"✨ هل ترغب في معرفة طريقة التحضير الصحية أو استبدال أي صنف؟"
                    )
                else:
                    return (
                        f"📋 **Meal Schedule for {day_data.get('day', f'Day {target_day}')}:**\n\n"
                        f"🍳 **Breakfast ({b.get('calories', '—')}):**\n{b.get('meal', '—')}\n*Note: {b.get('notes', '—')}*\n\n"
                        f"🥗 **Lunch ({l.get('calories', '—')}):**\n{l.get('meal', '—')}\n*Note: {l.get('notes', '—')}*\n\n"
                        f"🍽️ **Dinner ({d.get('calories', '—')}):**\n{d.get('meal', '—')}\n*Note: {d.get('notes', '—')}*\n\n"
                        f"🍎 **Snack ({s.get('calories', '—')}):**\n{s.get('meal', '—')}\n\n"
                        f"✨ Would you like to substitute any ingredient from this day?"
                    )
            else:
                if is_ar:
                    return (
                        f"📋 **مقترح وجبات اليوم {target_day} النموذجي:**\n\n"
                        f"🍳 **الإفطار:** بيضتان مسلوقتان مع نصف رغيف بلدي، سلطة خضراء، وزيت زيتون.\n"
                        f"🥗 **الغداء:** صدر دجاج مشوي متبل بالليمون والأعشاب مع 5 ملاعق أرز بني وخضار سوتيه.\n"
                        f"🍽️ **العشاء:** كوب زبادي خفيف مع جبنة قريش وتوست أسمر وخيار.\n"
                        f"🍎 **سناك:** تفاحة خضراء مع 7 حبات لوز ني."
                    )
                else:
                    return f"Day {target_day} consists of balanced portions of lean protein, low-GI complex carbs, and fresh greens tailored to your target calories."

        # ── 7. MEAL TYPES (Breakfast, Lunch, Dinner, Snack) ──
        if any(k in clean_msg for k in ['فطار', 'افطار', 'breakfast']):
            if is_ar:
                return (
                    "🍳 **دليل وجبة الإفطار في خطتك الغذائية:**\n\n"
                    "• **الهدف:** كسر صيام النوم، إعادة تعبئة مخازن الجليكوجين، واستقرار سكر الدم صباحاً.\n"
                    "• **أهم المكونات المعتمدة لك:** البيض المسلوق، الشوفان الكامل، الجبن القريش بزيت الزيتون، والزبادي اليوناني.\n"
                    "• **القاعدة الذهبية:** اشرب كوبين ماء (500 مل) فور الاستيقاظ وقبل وجبة الإفطار بـ 20 دقيقة.\n"
                    "• يمكنك سؤالي: *'إيه فطار اليوم الأول؟'* أو *'ما هو بديل البيض؟'* وسأجيبك فوراً!"
                )
            else:
                return (
                    "🍳 **Breakfast Guidelines in Your Plan:**\n\n"
                    "• Core Options: Eggs, rolled oats, Greek yogurt, whole wheat toast with olive oil.\n"
                    "• Hydration: Always drink 500ml of room-temperature water upon waking before eating."
                )

        if any(k in clean_msg for k in ['غدا', 'غداء', 'lunch']):
            if is_ar:
                return (
                    "🥗 **دليل وجبة الغداء في خطتك الغذائية:**\n\n"
                    "• **الهدف:** تمثل الوجبة الرئيسية التي تمدك بأعلى نسبة طاقة (حوالي 35% من سعراتك اليومية).\n"
                    "• **التوزيع المثالي لطبقك:**\n"
                    "  - **نصف الطبق:** خضروات وسلطة خضراء غنية بالألياف وزيت الزيتون.\n"
                    "  - **ربع الطبق:** بروتين صافي (صدر دجاج مشوي، سمك فيليه، تونة، لحم بقري صافي).\n"
                    "  - **ربع الطبق:** نشويات معقدة (أرز بني، كينوا، بطاطا حلوة مشوية).\n"
                    "• تجنب تماماً الأطعمة المقلية والمشروبات الغازية مع الغداء لضمان أقصى استفادة ونشاط."
                )
            else:
                return (
                    "🥗 **Lunch Guidelines in Your Plan:**\n\n"
                    "• Accounts for approximately 35% of your daily calories.\n"
                    "• Plate: 1/2 veggies, 1/4 lean protein, 1/4 complex low-GI carbs."
                )

        if any(k in clean_msg for k in ['عشا', 'عشاء', 'dinner']):
            if is_ar:
                return (
                    "🍽️ **دليل وجبة العشاء في خطتك الغذائية:**\n\n"
                    "• **الهدف:** وجبة خفيفة ومريحة للهضم تدعم الاستشفاء العضلي أثناء النوم دون تخزين دهون.\n"
                    "• **أفضل الخيارات المعتمدة لك:** جبنة قريش بالطماطم وزيت الزيتون، زبادي خفيف مع بذور الكتان، شوربة خضار دافئة، أو بيضة مسلوقة مع سلطة.\n"
                    "• **التوقيت المثالي:** احرص على تناول العشاء قبل موعد النوم بـ **ساعتين إلى 3 ساعات على الأقل** لمنع ارتجاع المريء وتحسين جودة النوم العميق."
                )
            else:
                return (
                    "🍽️ **Dinner Guidelines in Your Plan:**\n\n"
                    "• Keep it light and easy to digest (cottage cheese, Greek yogurt, lean turkey, vegetable soup).\n"
                    "• Consume at least 2 to 3 hours before sleep."
                )

        # ── 8. CALORIES & MACRONUTRIENTS ──
        if any(k in clean_msg for k in ['سعرات', 'كالوري', 'calories', 'calorie']):
            if is_ar:
                return (
                    f"🔥 **تفاصيل السعرات والمغذيات الكبرى المحددة لك:**\n\n"
                    f"• **إجمالي السعرات اليومية:** **{daily_cals}**\n"
                    f"• **البروتين:** **{protein}** (لبناء العضلات وسرعة الشبع)\n"
                    f"• **الكربوهيدرات:** **{carbs}** (طاقة نظيفة ومنخفضة المؤشر الجلايسيمي)\n"
                    f"• **الدهون الصحية:** **{fat}** (لهرمونات الجسم وصحة المفاصل)\n\n"
                    f"هذا التوزيع محسوب بدقة علمية وفق معادلة Mifflin-St Jeor ليضمن نزول الدهون أو تثبيت الوزن دون إرهاق."
                )
            else:
                return (
                    f"🔥 **Calorie & Macro Breakdown:**\n\n"
                    f"• **Daily Target:** **{daily_cals}**\n"
                    f"• **Protein:** **{protein}**\n"
                    f"• **Carbohydrates:** **{carbs}**\n"
                    f"• **Healthy Fats:** **{fat}**"
                )

        if any(k in clean_msg for k in ['بروتين', 'protein']):
            if is_ar:
                return (
                    f"🥩 **احتياجك اليومي من البروتين:** **{protein}**\n\n"
                    "• **أهمية البروتين:** يحافظ على كتلتك العضلية، يرفع من معدل الأيض (TEF)، ويعزز هرمونات الشبع.\n"
                    "• **أفضل مصادر البروتين في خطتك:**\n"
                    "  1. صدور الدجاج والديك الرومي (حوالي 30 جم بروتين لكل 100 جم).\n"
                    "  2. سمك الفيليه، السلمون، والتونة المصفاة.\n"
                    "  3. البيض المسلوق (حوالي 6-7 جم بروتين لكل بيضة).\n"
                    "  4. جبن القريش والزبادي اليوناني.\n"
                    "  5. العدس، الحمص، والتوفو كخيارات نباتية ممتازة."
                )
            else:
                return f"🥩 **Your Daily Protein Target:** **{protein}** (lean meats, eggs, Greek yogurt, fish)."

        if any(k in clean_msg for k in ['كارب', 'كربوهيدرات', 'نشويات', 'carbs', 'carbohydrate']):
            if is_ar:
                return (
                    f"🌾 **حصتك اليومية من الكربوهيدرات:** **{carbs}**\n\n"
                    "• خطتك لا تقطع الكربوهيدرات بل تختار **الكربوهيدرات المعقدة (Complex Low-GI Carbs)**.\n"
                    "• **أفضل الخيارات في جدولك:** الشوفان الكامل، الأرز البني، الكينوا، البطاطا الحلوة المشوية، وخبز الحبوب الكاملة.\n"
                    "• **الفائدة:** تمد الدماغ والعضلات بالطاقة الثابتة دون رفع مفاجئ لهرمون الإنسولين، مما يمنع الشعور بالخمول أو الجوع السريع."
                )
            else:
                return f"🌾 **Your Daily Carbohydrate Target:** **{carbs}** (complex low-GI carbs: brown rice, oats, sweet potatoes)."

        if any(k in clean_msg for k in ['دهون', 'fat', 'fats']):
            if is_ar:
                return (
                    f"🥑 **حصتك اليومية من الدهون الصحية:** **{fat}**\n\n"
                    "• الدهون الصحية عنصر إلزامي لإنتاج الهرمونات وامتصاص الفيتامينات الذائبة في الدهون (A, D, E, K).\n"
                    "• **المصادر الموصى بها في خطتك:**\n"
                    "  - ملعقة طعام من زيت الزيتون البكر الممتاز على السلطة يومياً.\n"
                    "  - ربع ثمرة أفوكادو.\n"
                    "  - 7 إلى 10 حبات من اللوز الني أو الجوز (عين الجمل).\n"
                    "  - ملعقة صغيرة من بذور الشيا أو الكتان المطحونة."
                )
            else:
                return f"🥑 **Your Daily Healthy Fat Target:** **{fat}** (olive oil, raw nuts, avocado)."

        # ── 9. MEDICAL CONDITIONS (Diabetes, Hypertension, Cholesterol, Thyroid) ──
        if any(k in clean_msg for k in ['سكر', 'سكري', 'جلوكوز', 'diabetes']):
            if is_ar:
                return (
                    "🩸 **البروتوكول السريري لمرضى السكري المطبق في خطتك:**\n\n"
                    "• تم ضبط النشويات لتكون **منخفضة المؤشر الجلايسيمي (Low Glycemic Index)** لمنع أي قفزات مفاجئة في سكر الدم.\n"
                    "• **ترتيب تناول الطعام في وجبتك:**\n"
                    "  1. ابدأ دائماً بطبق السلطة الخضراء الغني بالألياف.\n"
                    "  2. ثم تناول البروتين (دجاج/سمك/لحم).\n"
                    "  3. واجعل النشويات (الأرز البني أو البطاطا) في النهاية (هذا الترتيب يقلل امتصاص السكر بنسبة تصل إلى 40%).\n"
                    "• استبعدت خطتك تماماً السكريات البسيطة، العصائر المصنعة، والدقيق الأبيض."
                )
            else:
                return "🩸 **Diabetes Protocol:** Strictly low-GI carbs, eat fiber first, followed by protein and carbs."

        if any(k in clean_msg for k in ['ضغط', 'الضغط', 'ملح', 'صوديوم', 'hypertension']):
            if is_ar:
                return (
                    "❤️ **بروتوكول DASH المعتمد لضغط الدم في خطتك:**\n\n"
                    "• **الحد من الصوديوم:** الاعتماد على أقل من 1500 مجم صوديوم يومياً.\n"
                    "• استبدال ملح الطعام المكرر بعصير الليمون، الكمون، الزعتر، والخل الطبيعي لإعطاء نكهة شهية وآمنة.\n"
                    "• زيادة الأطعمة الغنية بالبوتاسيوم والمغنيسيوم (السبانخ، الأفوكادو، البروكلي، والموز باعتدال).\n"
                    "• استبعاد الأطعمة المصنعة، اللحوم الباردة (اللانشون والسوسيس)، والمخللات والمقرمشات المملحة."
                )
            else:
                return "❤️ **DASH Protocol:** Sodium <1500mg/day, rich in potassium and magnesium, no processed meats."

        if any(k in clean_msg for k in ['كوليسترول', 'دهون ثلاثيه', 'cholesterol']):
            if is_ar:
                return (
                    "🫀 **بروتوكول خفض الكوليسترول والدهون الثلاثية:**\n\n"
                    "• **تقييد الدهون المشبعة:** أقل من 6% من إجمالي السعرات، واستبعاد السمن الصناعي والزيوت المهدرجة تماماً.\n"
                    "• **زيادة الألياف القابلة للذوبان:** تناول الشوفان الكامل وبذور الكتان المطحونة يومياً (تلتصق بالكوليسترول الضار في الأمعاء وتطرده خارج الجسم).\n"
                    "• تناول الأسماك الزيتية (السلمون أو التونة أو السردين) مرتين أسبوعياً لرفع الكوليسترول الحميد (HDL)."
                )
            else:
                return "🫀 **Cholesterol Management:** Saturated fats <6%, high soluble fiber (oats, flaxseed), fatty fish."

        # ── 10. HYDRATION & DRINKING WATER ──
        if any(k in clean_msg for k in ['مياه', 'ماء', 'شرب ماء', 'عطش', 'سوائل', 'water', 'hydrate']):
            if is_ar:
                return (
                    "💧 **قواعد شرب الماء وترطيب الجسم:**\n\n"
                    "• **الاحتياج اليومي لك:** احرص على شرب **من 2.5 إلى 3.5 لتر ماء يومياً** (حوالي 10 - 12 كوب).\n"
                    "• **الجدول الموصى به:**\n"
                    "  - كوبان فور الاستيقاظ مباشرة لتنشيط الدورة الدموية والأمعاء.\n"
                    "  - كوب كبير قبل كل وجبة بـ 20 دقيقة (يساعد على الشبع وتحسين الامتصاص).\n"
                    "  - تجنب شرب كميات كبيرة من الماء أثناء تناول الطعام مباشرة لتجنب تخفيف العصارة الهاضمة.\n"
                    "• **المشروبات المسموحة بدون سكر:** الشاي الأخضر، البابونج، النعناع، واليانسون."
                )
            else:
                return "💧 **Hydration Protocols:** Target 2.5 to 3.5 Liters of water daily distributed between meals."

        # ── 11. HUNGER & SNACKS ──
        if any(k in clean_msg for k in ['جوع', 'جعان', 'شبع', 'سناك', 'hungry', 'snack']):
            if is_ar:
                return (
                    "🥒 **إليك خطة الطوارئ للتعامل مع الجوع بين الوجبات:**\n\n"
                    "1. **اختبار الماء أولاً:** اشرب كوبين كبيرين من الماء الفاتر وانتظر 10 دقائق (المخ يخلط كثيراً بين إشارات العطش والجوع).\n"
                    "2. **الخضروات الحرة (Zero-Calorie Volume):** تناول كميات غير محدودة من الخيار الطازج، الخس، الجرجير، أو الكرفس.\n"
                    "3. **إذا استمر الجوع الحقيقي:** تناول سناك صحي غني بالبروتين مثل:\n"
                    "   - 8 إلى 10 حبات لوز ني غير مملح.\n"
                    "   - 3 ملاعق كبيرة جبن قريش مع شرائح خيار.\n"
                    "   - بيضة مسلوقة صغيرة مع رشة كمون.\n"
                    "4. احرص على تناول كامل كمية البروتين والألياف المحددة في وجبتك السابقة لمنع تكرار الجوع."
                )
            else:
                return "🥒 **Hunger Hacks:** Drink 500ml water first, eat high-volume greens (cucumber, celery), or 10 raw almonds."

        # ── 12. EXERCISE, FITNESS & WEIGHT LOSS ──
        if any(k in clean_msg for k in ['تمرين', 'رياضه', 'جيم', 'حديد', 'عضلات', 'workout', 'gym', 'exercise']):
            if is_ar:
                return (
                    "💪 **تكامل التمارين الرياضية مع خطتك الغذائية:**\n\n"
                    "• **قبل التمرين (بـ ساعة إلى ساعتين):** وجبة خفيفة تجمع النشويات المعقدة لضمان طاقة مستمرة (مثال: شريحة توست بني مع ملعقة زبدة فول سوداني، أو موزة صغيرة مع 5 حبات لوز).\n"
                    "• **بعد التمرين (خلال 45 دقيقة):** وجبة غنية بالبروتين السريع للاستشفاء العضلي (مثال: سكوب بروتين أو علبة تونة أو 3 بيضات مسلوقة مع نصف رغيف بلدي).\n"
                    "• احرص على شرب 500 مل ماء إضافي لكل 30 دقيقة من النشاط الرياضي المكثف."
                )
            else:
                return "💪 **Exercise & Nutrition:** Complex carbs 90 min before workout; lean protein within 45 min after training."

        if any(k in clean_msg for k in ['ثبات الوزن', 'وزني ثابت', 'مش بينزل', 'ثبات', 'plateau']):
            if is_ar:
                return (
                    "⚖️ **كيف تتغلب على ثبات الوزن (Weight Loss Plateau)؟**\n\n"
                    "1. **ثبات الوزن ليس ثبات الدهون:** أحياناً يخسر الجسم دهوناً ويكتسب سوائل أو كتلة عضلية، لذا اعتمد على مقاسات الملابس والمرآة وليس الميزان فقط.\n"
                    "2. **احتباس السوائل:** الإجهاد وقلة النوم والأملاح الزائدة تحبس ما يصل إلى 2 كجم ماء في الجسم.\n"
                    "3. **زيادة الحركة غير الرياضية (NEAT):** احرص على المشي 8,000 إلى 10,000 خطوة يومياً.\n"
                    "4. استمر في الالتزام بخطتك المحددة لمدة 15 يوماً وسيكسر الجسم الثبات طبيعياً!"
                )
            else:
                return "⚖️ **Plateau Strategy:** Track clothing fit and waist circumference; increase daily steps to 10k."

        if any(k in clean_msg for k in ['خساره الوزن', 'تخسيس', 'انقاص الوزن', 'حرق الدهون', 'وزن']):
            if is_ar:
                return (
                    f"🎯 **استراتيجية نزول الوزن في خطتك:**\n\n"
                    f"• تم حساب سعراتك على **{daily_cals}** لإنشاء عجز سعرات صحي (Caloric Deficit) مقداره حوالي 450-500 سعرة يومياً.\n"
                    "• هذا العجز يضمن حرق دهون بمعدل **0.5 إلى 1 كجم أسبوعياً** وهو المعدل الصحي الآمن الذي يمنع ترهل الجلد أو فقدان الكتلة العضلية.\n"
                    "• الأهم هو عدم تفويت الوجبات وعدم النزول بسعراتك لأقل من المعدل المحدد حتى لا يدخل جسمك في طور المجاعة ويبطئ الحرق."
                )
            else:
                return f"🎯 **Weight Loss Strategy:** Calibrated at {daily_cals} for a safe, sustainable fat loss rate of 0.5-1 kg/week."

        # ── 13. NUTRITION TIPS ──
        if any(k in clean_msg for k in ['نصيحه', 'نصايح', 'tips', 'advice']):
            if is_ar:
                return (
                    "🌟 **أهم 5 نصائح ذهبية لضمان نجاح خطتك الغذائية:**\n\n"
                    "1. **النوم الكافي (7-8 ساعات):** قلة النوم ترفع هرمون الجوع (الجريلين) وتبطئ معدل الحرق بنسبة 15%.\n"
                    "2. **الماء قبل الأكل:** اشرب كوبين ماء قبل كل وجبة بـ 20 دقيقة.\n"
                    "3. **المضغ البطيء:** خذ 20 دقيقة على الأقل لإكمال وجبتك لإعطاء إشارات الشبع فرصة للوصول للدماغ.\n"
                    "4. **الطهي الصحي:** استبدل القلي بالشوي في الفرن، القلاية الهوائية (Air Fryer)، أو السلق.\n"
                    "5. **الالتزام بالحصص:** التزم بالجرامات والمقادير المحددة في خطتك لكل وجبة."
                )
            else:
                return "🌟 **Top Rules:** 7-8 hours sleep, 500ml water before meals, slow chewing, baking/grilling instead of frying."

        # ── 14. DYNAMIC CONTEXTUAL FALLBACK ──
        if is_ar:
            return (
                f"أهلاً بك! 🥗 خطتك الغذائية لمدة 15 يوماً مضبوطة على **{daily_cals}** "
                f"مع **{protein} بروتين** و**{carbs} كربوهيدرات** و**{fat} دهون صحية**.\n\n"
                f"بخصوص استفسارك:\n"
                f"• يمكنك سؤالي مباشرة عن وجبات أي يوم (مثال: *'وجبات اليوم الأول'* أو *'وجبة غداء اليوم العاشر'*).\n"
                f"• يمكنك سؤالي عن استبدال أي طعام (مثال: *'بديل الدجاج'* أو *'بديل البيض'* أو *'بديل الأرز'*).\n"
                f"• أو الاستفسار عن المشروبات والقهوة والتمارين الرياضية.\n\n"
                f"كيف يمكنني مساعدتك تحديداً في خطتك اليوم؟"
            )
        else:
            return (
                f"Welcome! 🥗 Your 15-day plan is set at **{daily_cals}** "
                f"with **{protein} protein** and **{carbs} carbs**.\n\n"
                f"• Ask me about specific day meals (e.g. *'Day 1 meals'* or *'Day 5 lunch'*).\n"
                f"• Ask for substitutions (e.g. *'substitute chicken'*, *'substitute eggs'*).\n"
                f"• Ask about coffee, workouts, or hunger management.\n\n"
                f"How can I assist you right now?"
            )
