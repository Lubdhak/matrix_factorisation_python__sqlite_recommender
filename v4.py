from utility import *

TRAIN_MODEL = False
INCLUDE_NON_PERSONA_ITEMS = True
REPEAT_SKIPPED_ITEMS = True
CONSIDER_ITEM_IF_P_RATING_IS_ABOVE = 3.0
TOP_N_ITEMS = 100

if __name__ == '__main__':
    print("🔮 ProductRoulette 🔮")
    uname = input("Enter uname")
    persona = input("Enter persona")
    product_id = True
    user_id = login(uname,persona)
    if user_id:
        rec_for_user_id = make_recommendations(user_id,persona,TOP_N_ITEMS)
        # print("Recommended Items:",rec_for_user_id)
        while product_id:
            product_id,rec_for_user_id = viewproduct(user_id,persona,rec_for_user_id)
            if product_id:
                while True:
                    ui = input("Enter Rating from 1 to 5 or N to view next..\n\n\n\n\n\n")
                    if ui not in ['n', '1', '2', '3', '4', '5']:
                        print("Valid Input Please")
                    else:
                        if ui == 'n':
                            score = 0
                        else:
                            score = int(ui)
                        rateproduct(user_id, product_id, score)
                        break