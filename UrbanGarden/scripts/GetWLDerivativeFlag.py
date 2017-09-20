#====================================================================================================
# Ministere des Peches et Oceans Canada / Department of Fisheries and Oceans Canada
# Service Hydrographique du Canada / Canadian Hydrographic Service
# Institut Maurice Lamontagne - Maurice Lamontagne Institute 
# 850, route de la Mer, Mont-Joli, Canada | 850 route de la Mer, Mont-Joli, Canada
#
#
# Project    : PPO - Volet produits dynamiques / OPP - Dynamical products component. 
#
# File       : GetWLDerivativeFlag.py
#
# Creation   : Sept. 2017 - G.Mercier - SHC / CHS - IML / MLI - Mont-Joli.
#
# Description:     Cette fonction permet de determiner la tendance(stable, diminution, augmentation) 
#              de cinq niveaux d'eau passes en argument sous forme de liste ordonnee dans le temps et 
#              ayant une meme difference temporelle de 15mins(900s) entre ses valeurs successives. Un
#              seuil(Threshold) de decision de 0.2 metres/heures est utilise par defaut a moins que ce 
#              seuil ne soit passe comme 2eme argument a la fonction.
#
#                  La tendance en metres/heures est determinee en calculant la pente de la regression 
#              lineaire simple entre les increments de temps (variable independante) et les niveaux
#              d'eau (variable dependante). Cette tendance est ensuite comparee a la valeur du seuil
#              (qui doit evidemment etre en metres/heures) pour retourner le bon code de tendance.  
#
#              NOTE: Les niveaux d'eau de la liste WLList prise en arguments doivent obligatoirement 
#                    etre de type float et non des strings. Cela vaut aussi pour le seuil. 
#
#              / 
#
#                  This function gives the trend(steady, decreasing or increasing) for a list 
#              of five water levels passed as a time ordered list argument and having an equal 
#              fixed time difference of 15mins(900s) between its successive values. The threshold
#              for the decision could also be passed as an optional argument or the default
#              0.2 meters/hours is used if the water levels list is the only argument to the function.
#
#                  The trend in meters/hours is determined with the computation of the simple linear 
#              regression slope coefficient between the time offsets (independant variable) and the water 
#              levels (dependant variable). This trend is then compared to the threshold value (which must 
#              obviously be in meters/hours) to return the appropriate water level trend flag. 
#
#              NOTE: The water levels of the list WLList must already be of type float and not of type
#                    string. The Threshold must also already be of type float. 
#  
#====================================================================================================

def GetWLDerivativeFlag(WLList,Threshold=0.2):

   import sys
   import math

   #---- Use a dictionary to define water levels trend flags:

   TREND_FLAGS = { "STEADY" : 0, "DECREASING" : 1, "INCREASING" : 2, "UNKNOWN" : 3 }

   #---- NOTE : We need to have a hard-coded list of five time offsets in decimal hours from the central 
   #            date-time stamp so the first two elements of this list have to be negative here to
   #            get the right results.
   #
   #     TODO: Pass an argument for the time offset in seconds between the successive water levels values 
   #           in the list and build a dynamic hourlyOffsets list with this argument.
   #
   #           This would be more flexible and would allow for the use of water levels lists of different 
   #           odd(mandatory) lengths >= 3 and would also allow for the use of different time offsets (as 
   #           low as 180 seconds) between successive water levels values.

   hourlyOffsets= [ -0.5, -0.25, 0.0, 0.25, 0.5 ]

   ret= -1 #---- To signal an error.

   #---- We need 5 water levels otherwise it is an error:
   if len(WLList) == 5:

      ret= TREND_FLAGS["STEADY"] #---- default water level trend flag -> "STEADY"

      numAcc= 0.0 #---- Accumulator for the numerator of the linear regression slope coefficient.
      denAcc= 0.0 #---- Accumulator for the denominator of the linear regression slope coefficient.     

      it= 0

      #---- Here we assume that the five water levels are in an increasing time order i.e. WLs[0] date-time stamp 
      #     is in the past compared to date-time stamp of WLs[1] and so on. We also assume that successive 
      #     WLs have an equal time difference of 15 minutes(900 seconds) to get the water level trend in 
      #     m/hour centered on the date-time stamp of the WLs which is at index 2(i.e. the 2rd element of the WLs)  

      for wl in WLList:

         tOfst= hourlyOffsets[it]

         numAcc += tOfst*wl
         denAcc += tOfst*tOfst #---- No need to do this accumulation in denAcc if hourlyOffsets list is hard-coded but
                               #     it could eventually be passed as an argument so keep it as it is.        

         it= it+1

      #print "numAcc ="+str(numAcc)
      #print "denAcc ="+str(denAcc)

      #---- Get the linear regression slope:
      derTrendPerHour= numAcc/denAcc

      #print "derTrendPerHour aft ="+str(derTrendPerHour)

      absDerTrendPerHour= math.fabs(derTrendPerHour)
       
      #---- NOTE: We assume that Threshold argument is in meters/hours but we do not assume that it is positive here:
      if absDerTrendPerHour > math.fabs(Threshold):

         if derTrendPerHour < 0.0:

            ret= TREND_FLAGS["DECREASING"] 

         else:

            ret= TREND_FLAGS["INCREASING"]
   else:

      #---- -1 is returned if water levels list don't have 5 elements: 
      sys.stderr.write("ERROR: WLList arg. must have 5 elements !\n")

   return ret


         
