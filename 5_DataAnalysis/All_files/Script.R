setwd("/Users/Varun/Desktop/VarunSah/Github/DataScience/5_Analysis")
indata<-read.csv("products.csv", header = TRUE);
sink(file = "Statistical_Tests_Output.txt", append = FALSE, type = c("output", "message"), split = TRUE);
age_iucdAcceptance <- subset(indata, select=c(5,17))
bin_age_iucdAcceptance <- cbind(age_iucdAcceptance, rating_bin = cut(age_iucdAcceptance$AMAZON_RATING_AVG, breaks = c (-Inf, 2.5, Inf)));
bin_age_iucdAcceptance <- cbind(bin_age_iucdAcceptance, price_bin = cut(age_iucdAcceptance$PRICE, breaks = c (-Inf, 150, Inf)));
chi_age_iucdAcceptance <- chisq.test(table(bin_age_iucdAcceptance[3:4]));
chi_age_iucdAcceptance
chi_age_iucdAcceptance$observed
chi_age_iucdAcceptance$expected;
chi_age_iucdAcceptance$residual;
fisher_age_iucdAcceptance<- fisher.test(table(bin_age_iucdAcceptance[3:4]));
fisher_age_iucdAcceptance;
sink()