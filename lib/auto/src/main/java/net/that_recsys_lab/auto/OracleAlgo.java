package net.that_recsys_lab.auto;

import com.google.common.collect.BiMap;
import net.librec.common.LibrecException;
import net.librec.data.convertor.TextDataConvertor;
import net.librec.math.structure.SparseMatrix;
import net.librec.recommender.AbstractRecommender;
import net.librec.recommender.item.ItemEntry;
import net.librec.recommender.item.RecommendedItemList;
import net.librec.recommender.item.RecommendedList;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.*;

/**
 *
 * @WIL-Lab
 * @Aldo-OG
 *
 */
public class OracleAlgo extends AbstractRecommender {
    private SparseMatrix resultsMatrix;
    private TextDataConvertor resultsModel;
    private BiMap<Integer, String> userMappingInverse;
    private BiMap<Integer, String> itemMappingInverse;
    private BiMap<String, Integer> result_userMapping;
    private BiMap<String, Integer> result_itemMapping;

    @Override
    protected void trainModel() throws LibrecException {  // is this exception unnecessary?
        System.out.println("** Training model in OracleAlgo **");
        try {
            // Load resultsMatrix for this pass of OracleAlgo
            LoadResults();
            // Define Inverse mapping for this pass of OracleAlgo.
            // Flip requested inner ids to outer ids for split data.
            userMappingInverse = userMappingData.inverse();
            itemMappingInverse = itemMappingData.inverse();
            result_userMapping = resultsModel.getUserIds();
            result_itemMapping = resultsModel.getItemIds();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    @Override
    protected double predict(int userIdx, int itemIdx) throws LibrecException { // is this exception unnecessary?
        // This is the Raw ID.
        String user_raw = userMappingInverse.get(userIdx);
        String item_raw = itemMappingInverse.get(itemIdx);
        double predictedRating = Double.NaN; // Assume NaN
        try {
            int user_inner = result_userMapping.get(user_raw); // Use Raw ID to get inner id's for results matrix.
            int item_inner = result_itemMapping.get(item_raw);  // **Null pointer exception always when trying to get item...
            if(resultsMatrix.contains(user_inner,item_inner)) {  // If user and item ids are within...
                predictedRating = resultsMatrix.get(user_inner, item_inner);
                if (predictedRating == -2) {  // reached an empty user
                    predictedRating = 0.0;
                }
            }
        }
        catch(NullPointerException e){} // intentionally pass when looking for value which doesn't exist
        catch(Exception e){ e.printStackTrace(); }
        return predictedRating;
    }

    /**
     * recommend
     * * predict the ranking scores in the test data
     *
     * @return predictive rating matrix
     * @throws LibrecException if error occurs during recommending
     */
    @Override
    protected RecommendedList recommendRank() throws LibrecException {
        recommendedList = new RecommendedItemList(numUsers - 1, numUsers);
        ///// Edits in here
        HashSet<Integer> range10 = new HashSet<>();
        for(int i=1;i<=10;i++){ range10.add(i); }
        //////  Edits end here
        for (int userIdx = 0; userIdx < numUsers; ++userIdx) {
            Set<Integer> itemSet = trainMatrix.getColumnsSet(userIdx);
            for (int itemIdx = 0; itemIdx < numItems; ++itemIdx) {
                if (itemSet.contains(itemIdx)) {
                    continue;
                }
                double predictRating = predict(userIdx, itemIdx);
                if (Double.isNaN(predictRating)) {
                    continue;
                }
                this.recommendedList.addUserItemIdx(userIdx, itemIdx, predictRating);
            }
            this.recommendedList.topNRankItemsByUser(userIdx, topN);
            /////     Edits in here
            // Check the TopN Recs
            boolean flag = true;
            List<ItemEntry<Integer, Double>> currItemList = this.recommendedList.getItemIdxListByUserIdx(userIdx);
            for(ItemEntry<Integer, Double> entry: currItemList){
                int item = Integer.parseInt(itemMappingInverse.get(entry.getKey()));
                if (!range10.contains(item)){
                    flag = false;
                    break;
                }
            }
            // If the TopN values are only 1-10
            if (flag){
                ArrayList<ItemEntry<Integer, Double>> itemList = new ArrayList<>(10);
                for (Integer i=0;i<10;i++) {
                    //int i_outer = Integer.parseInt(itemMappingInverse.get(i));
                    int i_outer = itemMappingData.get(String.valueOf(i+1));
                    ItemEntry<Integer, Double> item = new ItemEntry<>(i_outer, 0.0);
                    itemList.add(i, item);
                }
                ((RecommendedItemList) recommendedList).setItemIdxList(userIdx, itemList);
            }
            ////// Edits end here
        }

        if(recommendedList.size()==0){
            throw new IndexOutOfBoundsException("No item is recommended, there is something error in the recommendation algorithm! Please check it!");
        }

        return recommendedList;
    }


    /**
     * ~ Auto-Method ~
     *
     * Loads result file and extract SparseTensor
     *
     * Assumes resultsMatrix exist data exists
     *
     * @throws ClassNotFoundException
     * @throws IOException
     * @throws LibrecException
     */
    private void LoadResults() throws FileNotFoundException {  // this should return an arraylist of doubles, not String
        // Determine path
        Integer cvSplit = Integer.parseInt(conf.get("data.splitter.cv.index", "1"));
        String path = conf.get("dfs.result.dir") + "/out-" + cvSplit + ".txt";
        AutoDataAppender tempResultModel = new AutoDataAppender(path);
        try {
            tempResultModel.processData();
        } catch (IOException e) {
            e.printStackTrace();
        }
        SparseMatrix temp = tempResultModel.getPreferenceMatrix();
        resultsMatrix = temp.clone();
        resultsModel = tempResultModel;
    }
}