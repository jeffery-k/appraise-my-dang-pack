# Appraise My Dang Pack V2

Appraise My Dang Pack is a companion tool for Dan Gheesling's [DangPacks](https://dangpacks.com).

## Context

Dang Cards are minted digital cards which represent various elements of cultural significance to Dan Gheesling's streaming community.
Mints of cards can contain features such as varying rarities, stamps, sleeves etc.
While Dang Cards are tradable, they have no intrinsic value material or virtual, so the fairness of a trade can only be judged by the subjective value the trading parties place on them.
The lack of a currency makes for an organic and human experience, which is great for sentimental types, but is an abomination to econ nerds.
Appraise My Dang Pack seeks to remedy this.

## Model

The premise of Appraise My Dang Pack is to use statistical methods to discern an estimate of the value of Dang Cards and the effect of features on said card's valuation.
We start with the assumption that every accepted trade is a fair trade, meaning that the value offered is equal to the value requested.
We create an estimator for the base value of all cards, the base value of all features on cards, and the "shiny" value for all features on cards.
The shiny value refers to an estimate of the multiplicative effect a feature has on a card's base value.

Using our estimators we devise the following formula for the value of a Dang Card:

    (base_card_value + sum(base_feature_value)) * (1 + sum(shiny_feature_value)

Where `sum` represents a summation over all features present on the card.

Given this model we use [scipy's optimization library](https://docs.scipy.org/doc/scipy/tutorial/optimize.html) to find the estimates which produce the fairest trades (the smallest squared difference between offered and requested values)

## Hosting

Appraise My Dang Pack is hosted using streamlit [here](https://appraise-my-dang-pack.streamlit.app/).

It can also be run locally on any system with python `3.12` or greater by cloning the repository and from within the root directory running

    pip3 install -r requirements.txt
    python3 -m streamlit run main.py
